#!/usr/bin/env python



acceptable = False

while acceptable == False:

	ask = int(input("blah: "))

	if ask == 1 or ask == 2:
		print("good : {}".format(ask))
		acceptable = True
	else:
		print("try again loser!: {}".format(ask))
		
		
print("moving on")