from difflib import SequenceMatcher
import os
import time, datetime

def compare_likes(pageid):

	if not os.path.exists("Reports"):
		os.makedirs("Reports")

	if not os.path.exists("Reports/"+pageid):
		os.makedirs("Reports/"+pageid)


	report = open("Reports/"+pageid+"/report-"+datetime.datetime.fromtimestamp(time.time()).strftime("%H-%M-%S")+".txt", "w")
	report.write("Ratios for page likers:"+"\n")

	fp = open("User Likes/"+pageid+"/users_likes.txt", "r").read().split("\n")

	#lines = fp.readlines()
	i = 0
	j = 0
	for i in range(0,len(fp)):
		for j in range(i+1,len(fp)-j):
			fp[i]=fp[i].rstrip()
			fp[j]=fp[j].rstrip()
			if (fp[i] == "profile.php" or fp[j] == "profile.php" or fp[j] == ""):
				continue

			print "Comparing " + fp[i] + " and " + fp[j]

			filename = "User Likes/"+pageid+"/"+fp[i]+'_pagesliked.txt'
			filename1 = "User Likes/"+pageid+"/"+fp[j]+'_pagesliked.txt'

			try:
				user1 = open(filename, "r")
			except IOError:
				continue

			try:
				user2 = open(filename1, "r")
			except IOError:
				continue

			#make sure file isn't empty
			if(user1 == "" or user2 == ""):
				continue

			match_count = 0
			page_count = 0
			page_count2 = 0

			for user1_page in user1:
				user2.seek(0)
				for user2_page in user2:
					page_count2 += 1
					if (user1_page == user2_page):
						match_count+=1

				page_count += 1

			total_user2 = 0
			if page_count != 0:
				total_user2 = page_count2/float(page_count)

			if page_count != 0:
				ratio = match_count/float(page_count+total_user2-match_count)

			if (ratio > 0.30):
				report.write(fp[i]+","+str(page_count)+","+fp[j]+","+str(total_user2)+",matches,"+str(match_count))
				report.write("\n")
		j = 0
	report.close()
		