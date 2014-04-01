from difflib import SequenceMatcher
import os
import time, datetime

#Function to compare all the user's likes from a page to find matches
def compare_likes(pageid):

	if not os.path.exists("Reports"):
		os.makedirs("Reports")

	if not os.path.exists("Reports/"+pageid):
		os.makedirs("Reports/"+pageid)

	#Create our report file to write to
	report = open("Reports/"+pageid+"/report-"+datetime.datetime.fromtimestamp(time.time()).strftime("%H-%M-%S")+".txt", "w")
	report.write("Ratios for page likers:"+"\n")

	fp = open("User Likes/"+pageid+"/users_likes.txt", "r").read().split("\n")

	i = 0
	j = 0
	
	#Start at the first user then grab the next user and begin comparing
	for i in range(0,len(fp)):
		for j in range(i+1,len(fp)-j):
			fp[i]=fp[i].rstrip()
			fp[j]=fp[j].rstrip()
			if (fp[i] == "profile.php" or fp[j] == "profile.php" or fp[j] == ""):
				continue

			print "Comparing " + fp[i] + " and " + fp[j]

			#Load in our lists of pages liked by users
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

			#Compare user1 page with user2 pages, then user1[1] page with user2 page
			for user1_page in user1:
				user2.seek(0)
				for user2_page in user2:
					page_count2 += 1
					if (user1_page == user2_page):
						match_count+=1

				page_count += 1

			total_user2 = 0
			#Amount of pages for user 2
			if page_count != 0:
				total_user2 = page_count2/float(page_count)
	
			#Get ratio
			if page_count != 0:
				ratio = match_count/float(page_count+total_user2-match_count)

			#If match is past .30 threshold, add to report file
			if (ratio > 0.30):
				report.write(fp[i]+","+str(page_count)+","+fp[j]+","+str(total_user2)+",matches,"+str(match_count))
				report.write("\n")
		j = 0
	report.close()
		
