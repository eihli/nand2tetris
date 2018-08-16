(defun run-test ()
  (interactive)
  (let ((default-directory "~/code/nand2tetris/src/jack_analyzer/"))
    (async-shell-command "python -m unittest discover")))

(global-set-key (kbd "C-c t") 'run-test)
