from difflib import SequenceMatcher
import os

def compare_likes(pageid):

	if not os.path.exists("Reports"):
		os.makedirs("Reports")

	if not os.path.exists("Reports/"+pageid):
		os.makedirs("Reports/"+pageid)

	report = open("Reports/"+pageid+"/report.txt", "w")
	report.write("Ratios for page likers:"+"\n")

	fp = open("User Likes/"+pageid+"/users_likes.txt", "r").read().split("\n")

	#lines = fp.readlines()
	i = 0
	j = 0
	for i in range(0,len(fp)):
		for j in range(i+1,len(fp)-j):
			if (fp[i] == "profile.php" or fp[j] == "profile.php"):
				continue

			print "Comparing " + fp[i] + " and " + fp[j]

			filename = "User Likes/"+pageid+"/"+fp[i]+'_pagesliked.txt'
			filename1 = "User Likes/"+pageid+"/"+fp[j]+'_pagesliked.txt'

			try:
				user1 = open(filename).read()
			except IOError:
				print ""

			try:
				user2 = open(filename1).read()
			except IOError:
				print ""

			#make sure file isn't empty
			if(user1 == "" or user2 == ""):
				continue

			m = SequenceMatcher(None, user1, user2)
			#print "Ratio between users " + line.rstrip() + " and " + line2.rstrip() + ":" 
			if(fp[i] != fp[j]):
				ratio = float(m.ratio())
				if (ratio > 0.30):
					report.write("\n")
					report.write("User 1: "+ fp[i] + "\n")
					report.write("User 2: "+ j + "\n")
					report.write("Ratio: " + str(ratio) + " -- POSSIBLE BOT MATCH\n\n")

		j = 0

	report.close()
		