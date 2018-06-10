// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed.
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

	// Put your code here.

	// Loop forever
	(MAIN)

	// Get keyboard input
	@KBD

	// If key pressed, paint screen
	D=M
	@FILL
	D			;JNE

	// Blank code here
	(BLANK)
	@counter
	MD=0

	(BLOOP)
	@counter
	D=M
	@SCREEN
	A=A+D // Get address of screen mmap
	M=0 // blank it
	@counter
	M=D+1 // increment counter
	// if end: jump main
	@8191
	D=D-A
	@MAIN
	D			;JEQ
	@BLOOP
	0			;JMP

	// Fill code here
	(FILL)
	@counter
	MD=0

	(FLOOP)
	@counter
	D=M
	@SCREEN
	A=A+D // Get address of screen mmap
	M=-1 // fill it
	@counter
	M=D+1 // increment counter
	// if end: jump main
	@8191
	D=D-A
	@MAIN
	D			;JEQ
	@FLOOP
	0			;JMP


	@MAIN
	0			;JMP
