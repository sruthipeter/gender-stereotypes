# Gender Stereotypes Study
# Python Script to read in latin1 encoded csv data, and compute scales.
#
# Scale 1: Self Perceived Decision Making Power, assessed through 7 questions. 
#          These questions will be referred to as spdm_q1 through spdm_q7
#          Scoring : "you alone" = 5, 
#                    "you more than your partner" = 4
#                    "you and your partner exactly the same" = 3 
#                    "your partner more than you" = 2
#                    "your partner alone" = 1
# Scale 2: Index of Marital Satisfaction (IMS), assessed through 25 questions
#          These questions will be referred to as ims_q1 through ims_q25.
#          Scoring : "Rarely or none of the time" = 1
#                    "A little of the time" = 2
#                    "Sometime" = 3
#                    "A good part of the time" = 4
#                    "Most or all of the time" = 5
#          The scoring described should be reversed for ims_q1,ims_q3,ims_q5,ims_q8,ims_q9,ims_q11,ims_q13,ims_q16,
#          ims_q17,ims_q19,ims_q20,ims_21 and ims_q23.The final step is to subtract 25 from this sum. 
#          Scores below 30 are considered indicative of satisfaction with the relationship.
# Notes : 1. spdm_q7 was introduced half way through, so the first 15 participants did not answer this question.
#            We fill this missing data with the mode of all the other responses.
#         2. Reject all participants who answers sex as "female".
#         3. Reject other participants who did not answer either questionnaire completely.
# contact : sruthikurup@gmail.com
import sys
import pandas as pd

# CONSTANTS : Data Schema, Score Maps
data_schema = ['Timestamp','Above18','Consent','spdm_q1','spdm_q2','spdm_q3','spdm_q4','spdm_q5','spdm_q6','ims_q1','ims_q2','ims_q3','ims_q4','ims_q5','ims_q6','ims_q7','ims_q8','ims_q9','ims_q10','ims_q11','ims_q12','ims_q13','ims_q14','ims_q15','ims_q16','ims_q17','ims_q18','ims_q19','ims_q20','ims_q21','ims_q22','ims_q23','ims_q24','ims_q25','Gender','Age','num_male_siblings','num_female_siblings','f_influence','cousin_time','cousins_num_males','cousins_num_females','relationship_status','current_relationship_length','spdm_q7']
spdm_score_map = {"you alone":5,"you more than your partner":4,"you and your partner exactly the same":3,"your partner more than you":2,"your partner alone":1}
ims_score_map = {"Rarely or none of the time":1,"A little of the time":2,"Sometime":3,"A good part of the time":4,"Most or all of the time":5}
ims_reverse_score_map = {"Rarely or none of the time":5,"A little of the time":4,"Sometime":3,"A good part of the time":2,"Most or all of the time":1}

# Method to obtain the SPDM score for a row
def compute_spdm(row):
	score = 0
	prefix='spdm_q'
	for i in range(1,8):
		response = row[prefix+str(i)]
		if response in spdm_score_map:
			score = score + spdm_score_map[response]
		else:
			score = score + 3
	return score

# Method to obtain the IMS score for a row
def compute_ims(row):
	reverse_map_indices=[1,3,5,8,9,11,13,16,17,19,20,21,23]
	score = 0
	prefix='ims_q'
	for i in range(1,26):
		response = row[prefix+str(i)]
		if response in ims_score_map:
			if i in reverse_map_indices:
				score = score + ims_reverse_score_map[response]
			else:
				score = score + ims_score_map[response]
	return score-25

# Method to obtain the SPDM score on 0-100 scale
def compute_decisionPowerIndex(row):
	raw_score = compute_spdm(row)
	return float("{0:.2f}".format((raw_score*100.0)/35))

# Method to obtain SharedPowerIndex on a 0-100 scale
def compute_sharedPowerIndex(row):
	score = 0
	prefix='spdm_q'
	for i in range(1,8):
		response = row[prefix+str(i)]
		if (response == "you and your partner exactly the same") or (response not in spdm_score_map):
			score = score + 1
	return float("{0:.2f}".format((score*100.0)/7))

def compute_crossClassifyDecisionPowerIndex(row):
	shared_power_index = compute_sharedPowerIndex(row)
	decision_power_index = compute_decisionPowerIndex(row)
	if shared_power_index >= 66.0:
		return 'equalitarian'
	if shared_power_index < 33.0:
		return 'female-dominant'
	if shared_power_index < 66.0 and decision_power_index > 66.0:
		return 'male-dominant'
	if shared_power_index < 66.0 and decision_power_index > 33.0 and decision_power_index < 66.0:
		return 'divided-power'


data_file = open(sys.argv[1]) # Read in location of the csv data file as an argument 
data_df = pd.read_csv(data_file)
data_df.columns = data_schema

# Compute all the scales for all rows
data_df['spdm'] = data_df.apply(lambda row: compute_spdm (row),axis=1)
data_df['ims'] = data_df.apply(lambda row: compute_ims(row),axis=1)
data_df['DecisionPowerIndex'] = data_df.apply(lambda row: compute_decisionPowerIndex(row),axis=1)
data_df['SharedPowerIndex'] = data_df.apply(lambda row: compute_sharedPowerIndex(row),axis=1)
data_df['CrossClassifyDecisionPowerIndex'] = data_df.apply(lambda row: compute_crossClassifyDecisionPowerIndex(row),axis=1)

# Remove the two participants with incomplete responses
data_df = data_df.drop(data_df[data_df.ims < 0].index)

# Remove any female participants
data_df = data_df.drop(data_df[data_df.Gender=='Female'].index)

data_df.to_csv('output.csv')
print 'All scales computed. See output.csv'
