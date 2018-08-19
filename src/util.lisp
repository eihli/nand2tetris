(defun run-test (dir test)
  (let ((default-directory dir ))
    (async-shell-command
     (concat "python -m unittest " test))))

(defun run-compiler-test ()
  (interactive)
  (run-test
   "~/code/nand2tetris/src/jack_analyzer"
   "test_compiler.TestSubroutineDec"))

(defun run-pdb (test)
  (let ((default-directory "~/code/nand2tetris/src/jack_analyzer"))
    (pdb
     (concat "python -m unittest " test))))

(global-set-key (kbd "C-c t") 'run-compiler-test)
(global-set-key
 (kbd "C-c d")
 (lambda () (interactive) (run-pdb "test_compiler.TestSubroutineDec")))
