import ujson
import sqlite3
import os
import scipy.io
import sys

def get_database_data(db_filename):
    conn = sqlite3.connect(db_filename)
    cursor = conn.execute("SELECT datastring FROM turkdemo")
    data = []
    for row in cursor:
        if row[0] == None:
            continue
        s = ujson.loads(ujson.loads(ujson.dumps(row[0])))
        data.append(s)
    return data

def get_subject_data(raw_json):
    subject = {}
    subject['assignmentId'] = raw_json['assignmentId']
    subject['workerId'] = raw_json['workerId']
    subject['hitId'] = raw_json['hitId']
    for entry in raw_json['data']:
        if 'survey_new' in entry['trialdata']['trial_type']:
            ans = ujson.loads(entry['trialdata']['answer'])
            for field in ans:
                subject[field] = ans[field]
            break
    return subject
'''
def get_triplet_data(raw_json):
    triplets = []
    for entry in raw_json['data']:
        if 'custom_triplet' in entry['trialdata']['trial_type']:
            triplet = {}
            triplet['stimuli'] = ujson.loads(entry['trialdata']['stimulus'])
            triplet['stimuli'][1] = triplet['stimuli'][1][24:-4]
            triplet['stimuli'][0] = triplet['stimuli'][0][24:-4]
            triplet['stimuli'][2] = triplet['stimuli'][2][24:-4]
            triplet['pressed'] = ujson.loads(entry['trialdata']['pressed'])
            triplet['response'] = ujson.loads(entry['trialdata']['response'])
            triplet['type'] = entry['trialdata']['type']
            if (triplet['stimuli'][0] == triplet['stimuli'][1] or triplet['stimuli'][0] == triplet['stimuli'][2] or triplet['stimuli'][1] == triplet['stimuli'][2]):
                triplet['type'] = '3'
                if (triplet['response'][0]==triplet['response'][1]):
                    triplet['pressed'] = ['true','true']
                else:
                    triplet['pressed'] = ['false','false']
            if len(triplet['response']) > 2 and triplet['type'] != '3':
                triplet['response'] = list(set(triplet['response']))
            if len(triplet['response']) > 2 and triplet['type'] == '3':
                triplet['response'] =triplet['response'][:2]
            triplet['response'][0] = triplet['response'][0][24:-4]
            triplet['response'][1] = triplet['response'][1][24:-4]
            triplet['react_time'] = entry['trialdata']['rt']
            triplet['trial_index_global'] = entry['trialdata']['trial_index_global']
            triplet['set'] = entry['trialdata']['set']
            triplets.append(triplet)
    return triplets
'''
def get_single_data(raw_json):
    singleStims = []
    last = 0
    for entry in raw_json['data']:
        if 'attr_custom' in entry['trialdata']['trial_type']:
            singleStim = {}
            singleStim['stimuli'] = ujson.loads(entry['trialdata']['stimulus'])[0]
            singleStim['stimuli'] = singleStim['stimuli'][19:-4]
            singleStim['type'] = entry['trialdata']['type']
            '''
            if (singleStim['stimuli'][1] == singleStim['stimuli'][0]):
                singleStim['score'] = entry['trialdata']['catchy_answer']
                singleStim['type'] = '3'
                if (len(doublet['score'])< 1):
                    singleStim['score'] = 'false'
                else:
                    singleStim['score'] = 'true'
            else:
                if len(entry['trialdata']['attr_score'])< 1:
                    singleStim['score'] = 'invalid'
                    singleStim = []
                    break
                else:
                    singleStim['score'] = entry['trialdata']['attr_score'][0]
            '''
            if len(entry['trialdata']['attr_score'])< 1:
                singleStim['score'] = 'invalid'
                singleStim = []
                break
            else:
                singleStim['score'] = entry['trialdata']['attr_score'][0]
            singleStim['react_time'] = entry['trialdata']['rt']
            singleStim['trial_index_global'] = entry['trialdata']['trial_index_global']
            
            singleStim['set'] = entry['trialdata']['set']
            singleStims.append(singleStim)
    return singleStims

def parse(raw_json):
    subject_data = get_subject_data(raw_json)
    #triplet_data = get_triplet_data(raw_json)
    singleStim_data = get_single_data(raw_json)
    if len(singleStim_data)== 0:
        #triplet_data = []
        subject_data = []
    combined_data = {}
    combined_data['subject_data'] = subject_data
    #combined_data['triplet_data'] = triplet_data
    combined_data['singleStim_data'] = singleStim_data
    return combined_data

if __name__=='__main__':

    raw_jsons = get_database_data(sys.argv[1])
    if not os.path.exists('experiment_data'):
        os.makedirs('experiment_data')
    workerCounter = 1
    output_file_name_with_path = 'experiment_data/'
    with open(output_file_name_with_path +'subjectData.csv', 'w') as f:
        f.write('workerCounter,assignmentId,workerId,hitId,age,gender,sexual orientation,race,community\n')
    with open(output_file_name_with_path + 'singleStim.csv', 'w') as f:
        f.write('workerCounter,assignmentId,workerId,hitId,trial type,set,global index,reaction time,score,stimulus\n')

#    with open(output_file_name_with_path + 'triplet.csv', 'w') as f:
#        f.write('workerCounter,assignmentId,workerId,hitId,trial type,set,global index,reaction time,response1,response2,responseLoc1,responseLoc2,stimulus1,stimulus2,stimulus3\n')

    for raw_json in raw_jsons:
        print len(raw_json)
        data = parse(raw_json)
        #output_folder_name = str(workerCounter)
        with open(output_file_name_with_path + 'singleStim.csv', 'a') as f:
            for entry in data['singleStim_data']:
                f.write(str(workerCounter) + ',' + str(data['subject_data']['assignmentId']) + ',' +\
                        str(data['subject_data']['workerId']) + ',' +\
                        str(data['subject_data']['hitId']) + ',' + str(entry['type']) + ','+str(entry['set']) + ',' + str(entry['trial_index_global']) + ','+ str(entry['react_time']) +\
                    ',' + str(entry['score']) + ',')
#                concat_str = ""
#                for stimulus in entry['stimuli']:
#                    concat_str += str(stimulus) + ','
                f.write(str(entry['stimuli'])+ '\n')
#                f.write(concat_str[:-1] + '\n')
        '''
        with open(output_file_name_with_path + 'triplet.csv', 'a') as f:
            for entry in data['triplet_data']:
                f.write(str(workerCounter) + ',' + str(data['subject_data']['assignmentId']) + ',' +\
                       str(data['subject_data']['workerId']) + ',' +\
                       str(data['subject_data']['hitId']) + ',' + str(entry['type']) + ','+str(entry['set'])+ ',' +str(entry['trial_index_global']) + ','+ str(entry['react_time']) + ',')
                for pressed_image in entry['response']:
                    f.write(str(pressed_image) + ',')
                concat_str = ""
                for loc in entry['pressed']:
                    f.write(str(loc) + ',')
                concat_str = ""
                for stimulus in entry['stimuli']:
                    concat_str += str(stimulus) + ','
                f.write(concat_str[:-1] + '\n')
        '''
        if len(data['subject_data'])>0:
            with open('experiment_data/subjectData.csv', 'a') as f:
                f.write(str(workerCounter) + ',' + str(data['subject_data']['assignmentId']) + ',' +\
                    str(data['subject_data']['workerId']) + ',' +\
                    str(data['subject_data']['hitId']) + ',')
            try:
                val = data['subject_data']['age']
                with open('experiment_data/subjectData.csv', 'a') as f:
                    f.write(str(data['subject_data']['age']) + ',' +\
                            str(data['subject_data']['gender'][0]) + ',' +\
                            str(data['subject_data']['sexOri'][0]) + ',')
                    concat_str = ""
                    for item in data['subject_data']['race']:
                        concat_str += str(item) + ' '
                    f.write(concat_str[:-1] + ',')
                    concat_str = ""
                    for item in data['subject_data']['comRace']:
                        concat_str += str(item) + ' '
                    f.write(concat_str[:-1] + '\n')
            except KeyError:
                with open('experiment_data/subjectData.csv', 'a') as f:
                    f.write('debug,debug,debug,debug,debug\n')
            workerCounter += 1



    print 'Done'
    # haha = scipy.io.loadmat('experiment_data/debugX308O0_debugMNSB5X_debug7M6X1D.mat')
    # print haha['doublet_data']








