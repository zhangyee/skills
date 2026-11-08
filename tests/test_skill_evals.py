import importlib.util
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import skill_evals as ev


FAKE_CODEX = r'''#!/usr/bin/env python3
import json, os, pathlib, sys, time
args = sys.argv[1:]
if '--version' in args:
    print('codex-test 1'); sys.exit(0)
if '--help' in args:
    print('--ignore-user-config --ignore-rules --ephemeral --json'); sys.exit(0)
prompt = sys.stdin.read()
mode = os.environ.get('SKILL_EVAL_TEST_MODE', '')
if mode == 'sleep': time.sleep(3)
if mode == 'fail':
    print(json.dumps({'type':'turn.failed','error':{'message':'test failure'}})); sys.exit(5)
out = pathlib.Path(args[args.index('--output-last-message')+1])
if '--output-schema' in args:
    data = json.loads(prompt)
    if 'fixtures/input.md' in data['task']:
        assert 'fixtures/input.md' in data.get('input_files', [])
        assert (pathlib.Path.cwd()/'fixtures/input.md').read_text() == 'original fixture'
    checks = [{'index':i,'passed':True,'evidence':'The output contains the requested fact.'}
              for i in range(len(data['assertions']))]
    if mode == 'bad-grade': checks = []
    out.write_text(json.dumps({'expectations':checks}))
else:
    root = pathlib.Path.cwd()
    dep = root / '.agents/skills/unslop/SKILL.md'
    text = dep.read_text() if dep.exists() else 'NO_SKILL'
    if 'ASSERTION_SECRET' in prompt: raise SystemExit('rubric leaked into executor')
    out.write_text(text + '\n</script><script>alert(1)</script>')
    (root/'artifact.txt').write_text('generated artifact')
print(json.dumps({'type':'thread.started','thread_id':'test'}))
if mode != 'incomplete':
    print(json.dumps({'type':'turn.completed','usage':{'input_tokens':10,'cached_input_tokens':2,'output_tokens':5}}))
'''


class EvalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name, body in [('writing-docs', '[unslop](../unslop/SKILL.md)'), ('unslop', 'FROZEN_V1')]:
            path = self.root / 'skills' / name
            path.mkdir(parents=True)
            (path/'SKILL.md').write_text('---\nname: '+name+'\n---\n'+body)
        self.cases = self.root/'evals/writing-docs/cases.json'
        self.cases.parent.mkdir(parents=True)
        self.cases.write_text(json.dumps({'skill':'writing-docs','cases':[
            {'id':'one','prompt':'Rewrite the supplied sentence.','assertions':['ASSERTION_SECRET']}]}))
        self.binary = self.root/'fake-codex'
        self.binary.write_text(FAKE_CODEX)
        self.binary.chmod(0o755)
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        self.commit('baseline')

    def commit(self, message):
        subprocess.run(['git','-C',str(self.root),'add','skills'],check=True)
        subprocess.run(['git','-C',str(self.root),'-c','user.name=Eval Test',
                        '-c','user.email=eval@example.invalid','-c','core.hooksPath=/dev/null',
                        'commit','-qm',message],check=True)

    def tearDown(self):
        self.temp.cleanup()

    def comparison(self, **kwargs):
        return ev.create_comparison(self.root, 'writing-docs', 'none', 'working-tree', 'test-model', **kwargs)

    def test_run_preserves_versions_and_detects_tampering(self):
        run = self.comparison()
        (self.root/'skills/unslop/SKILL.md').write_text('edited source')
        snap = run/'versions/candidate'
        self.assertIn('FROZEN_V1', (snap/'skills/unslop/SKILL.md').read_text())
        ev.load_comparison(run)
        (snap/'skills/unslop/SKILL.md').write_text('tampered')
        with self.assertRaises(ev.EvalError): ev.load_comparison(run)

    def test_dependency_is_pinned_and_resume_skips_completed_runs(self):
        run = self.comparison(repeat=2)
        (self.root/'skills/unslop/SKILL.md').write_text('NEW_VERSION')
        self.assertTrue(ev.run_comparison(run, str(self.binary), timeout=5))
        results = ev.results(run)
        self.assertEqual(len(results), 4)
        for item in results:
            self.assertEqual(item['status'], 'completed')
            text = (run/item['output_file']).read_text()
            self.assertIn('FROZEN_V1' if item['variant']=='candidate' else 'NO_SKILL', text)
            self.assertEqual(item['tokens']['total_tokens'], 15)
            command = item['command']
            self.assertIn('--ignore-user-config', command)
            self.assertIn('project_doc_max_bytes=0', command)
            self.assertIn('plugins',command)
        before = [(r['id'],r['attempt']) for r in results]
        self.assertTrue(ev.run_comparison(run, str(self.binary), timeout=5))
        self.assertEqual(before, [(r['id'],r['attempt']) for r in ev.results(run)])

    def test_failed_execution_is_not_counted_as_a_pass_and_can_resume(self):
        run = self.comparison()
        with patch.dict(os.environ, {'SKILL_EVAL_TEST_MODE':'fail'}):
            self.assertFalse(ev.run_comparison(run, str(self.binary), timeout=5))
        summary = ev.build_report(run)
        self.assertEqual(summary['variants']['candidate']['failed'], 1)
        self.assertIsNone(summary['variants']['candidate']['assertion_pass_rate'])
        self.assertTrue(ev.run_comparison(run, str(self.binary), timeout=5))
        self.assertTrue(all(r['attempt']==2 for r in ev.results(run)))

    def test_empty_or_unfinished_trace_is_a_failure(self):
        run = self.comparison()
        with patch.dict(os.environ, {'SKILL_EVAL_TEST_MODE':'incomplete'}):
            self.assertFalse(ev.run_comparison(run, str(self.binary), timeout=5))
        self.assertTrue(all(r['status']=='failed' for r in ev.results(run)))

    def test_timeout_is_recorded(self):
        run = self.comparison()
        with patch.dict(os.environ, {'SKILL_EVAL_TEST_MODE':'sleep'}):
            self.assertFalse(ev.run_comparison(run, str(self.binary), timeout=0.1))
        self.assertTrue(all('timeout' in r['error'].lower() for r in ev.results(run)))

    def test_rubric_is_hidden_from_executor_and_grades_require_all_assertions(self):
        run = self.comparison()
        self.assertTrue(ev.run_comparison(run, str(self.binary), timeout=5))
        with patch.dict(os.environ, {'SKILL_EVAL_TEST_MODE':'bad-grade'}):
            self.assertFalse(ev.grade_comparison(run, str(self.binary), 'test-judge', timeout=5))
        self.assertIsNone(ev.build_report(run)['variants']['candidate']['assertion_pass_rate'])
        self.assertTrue(ev.grade_comparison(run, str(self.binary), 'test-judge', timeout=5))
        self.assertEqual(ev.build_report(run)['variants']['candidate']['assertion_pass_rate'], 1.0)

    def test_report_is_escaped_and_feedback_is_bound_to_the_run(self):
        run = self.comparison()
        ev.run_comparison(run, str(self.binary), timeout=5)
        summary = ev.build_report(run)
        html = (run/'report.html').read_text()
        self.assertNotIn('</script><script>alert(1)</script>', html)
        feedback = {'comparison_id':summary['comparison_id'],'reviews':[
            {'case_id':'one','repetition':1,'winner':'candidate','notes':'keeps the facts'}]}
        path = self.root/'feedback.json'
        path.write_text(json.dumps(feedback))
        ev.import_review(run, path)
        self.assertEqual(ev.build_report(run)['human_preferences']['candidate'],1)
        feedback['comparison_id']='another-comparison'
        path.write_text(json.dumps(feedback))
        with self.assertRaises(ev.EvalError): ev.import_review(run, path)

    def test_invalid_case_ids_and_traversal_fail_before_execution(self):
        data=json.loads(self.cases.read_text())
        data['cases'][0]['id']='../outside'
        self.cases.write_text(json.dumps(data))
        with self.assertRaises(ev.EvalError): self.comparison()

    def test_fixtures_and_dataset_are_frozen(self):
        fixture=self.cases.parent/'fixtures/input.md'
        fixture.parent.mkdir()
        fixture.write_text('original fixture')
        data=json.loads(self.cases.read_text())
        data['cases'][0]['prompt']='Rewrite fixtures/input.md without changing facts.'
        data['cases'][0]['files']=['fixtures/input.md']
        self.cases.write_text(json.dumps(data))
        run=self.comparison()
        fixture.write_text('edited fixture')
        self.cases.write_text('{}')
        ev.run_comparison(run,str(self.binary),timeout=5)
        for item in ev.results(run):
            self.assertEqual((run/item['workspace']/'fixtures/input.md').read_text(),'original fixture')
        self.assertTrue(ev.grade_comparison(run,str(self.binary),'test-judge',timeout=5))

    def test_missing_dependency_fails_before_execution(self):
        (self.root/'skills/writing-docs/SKILL.md').write_text('[missing](../missing/SKILL.md)')
        with self.assertRaises(ev.EvalError):
            ev.create_comparison(self.root,'writing-docs','none','working-tree','test-model')

    def test_git_commit_and_current_source_use_their_own_dependencies(self):
        original = ev.git_output(self.root,'rev-parse','HEAD').decode().strip()
        (self.root/'skills/unslop/SKILL.md').write_text('UNCOMMITTED')
        run=ev.create_comparison(self.root,'writing-docs','HEAD','working-tree','test-model')
        meta=ev.load_comparison(run)
        self.assertEqual(meta['variants']['baseline']['source']['commit'],original)
        self.assertEqual(meta['variants']['candidate']['source']['kind'],'working-tree')
        self.assertFalse((self.root/'.eval-snapshots').exists())
        (self.root/'skills/unslop/SKILL.md').write_text('EDITED_AGAIN')
        self.assertTrue(ev.run_comparison(run,str(self.binary),timeout=5))
        for item in ev.results(run):
            text=(run/item['output_file']).read_text()
            self.assertIn('FROZEN_V1' if item['variant']=='baseline' else 'UNCOMMITTED',text)

    def test_cli_compares_tag_with_current_source_without_manual_snapshot(self):
        subprocess.run(['git','-C',str(self.root),'tag','v1'],check=True)
        (self.root/'skills/unslop/SKILL.md').write_text('CURRENT')
        result=subprocess.run([sys.executable,'-B',str(SCRIPTS/'eval-skills.py'),
            '--root',str(self.root),'compare','--skill','writing-docs','--baseline','v1',
            '--model','test-model','--codex',str(self.binary)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        runs=list((self.root/'.eval-runs/writing-docs').iterdir())
        self.assertEqual(len(runs),1)
        meta=ev.load_comparison(runs[0])
        self.assertEqual(meta['variants']['baseline']['name'],'v1')
        self.assertEqual(meta['variants']['candidate']['name'],'working-tree')
        self.assertTrue((runs[0]/'report.html').is_file())
        self.assertFalse((self.root/'.eval-snapshots').exists())

    def test_two_commits_can_be_compared_and_invalid_ref_leaves_no_run(self):
        previous=ev.git_output(self.root,'rev-parse','HEAD').decode().strip()
        (self.root/'skills/unslop/SKILL.md').write_text('SECOND_COMMIT')
        self.commit('second version')
        run=ev.create_comparison(self.root,'writing-docs',previous,'HEAD','test-model')
        self.assertIn('FROZEN_V1',(run/'versions/baseline/skills/unslop/SKILL.md').read_text())
        self.assertEqual((run/'versions/candidate/skills/unslop/SKILL.md').read_text(),'SECOND_COMMIT')
        before=set((self.root/'.eval-runs/writing-docs').iterdir())
        with self.assertRaises(ev.EvalError):
            ev.create_comparison(self.root,'writing-docs','no-such-ref','working-tree','test-model')
        self.assertEqual(set((self.root/'.eval-runs/writing-docs').iterdir()),before)

    def test_no_history_reports_that_a_git_baseline_is_required(self):
        import shutil
        shutil.rmtree(self.root/'.git')
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        with self.assertRaisesRegex(ev.EvalError,'commit|提交'):
            ev.create_comparison(self.root,'writing-docs','HEAD','working-tree','test-model')

    def test_resume_rejects_a_changed_cli_version(self):
        run=self.comparison()
        ev.run_comparison(run,str(self.binary),timeout=5)
        self.binary.write_text(self.binary.read_text().replace('codex-test 1','codex-test 2'))
        with self.assertRaises(ev.EvalError): ev.run_comparison(run,str(self.binary),timeout=5)

    def test_invalid_fixture_schema_is_rejected(self):
        data=json.loads(self.cases.read_text())
        data['cases'][0]['files']='not-a-list'
        self.cases.write_text(json.dumps(data))
        with self.assertRaises(ev.EvalError): self.comparison()

    def test_orphan_execution_and_grading_directories_do_not_block_recovery(self):
        run=self.comparison()
        first=ev.results(run)[0]
        job=run/'jobs'/first['id']
        (job/'attempt-1/workspace').mkdir(parents=True)
        self.assertTrue(ev.run_comparison(run,str(self.binary),timeout=5))
        restored=next(r for r in ev.results(run) if r['id']==first['id'])
        self.assertEqual(restored['attempt'],2)
        self.assertTrue((job/'attempt-1/workspace').exists())
        (job/'grade-1/workspace').mkdir(parents=True)
        self.assertTrue(ev.grade_comparison(run,str(self.binary),'test-judge',timeout=5))
        restored=next(r for r in ev.results(run) if r['id']==first['id'])
        self.assertEqual(restored['grade_attempt'],2)


if __name__ == '__main__':
    unittest.main()
