#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on Fri Jun  9 15:31:01 2017

@author: vinay kusuma.
Can be reached at vinay@pieriandx.com
"""

import yagmail, csv, requests, urllib2, time, datetime, os, urllib
from requests.exceptions import ConnectionError
from lxml import html

print '\n'
asco_date = time.strftime("%B %d, %Y")
#asco_date = "July 10, 2010"
asco_dates = [datetime.datetime.strptime(asco_date, '%B %d, %Y') - datetime.timedelta(days=i) for i in range(8)]
asco_week = [day.strftime('%B %d, %Y') for day in asco_dates]                  
print asco_week             
clinvar_date = time.strftime("%b %d")
#clinvar_date = 'Jun 2'
clinvar_dates = [datetime.datetime.strptime(clinvar_date, '%b %d') - datetime.timedelta(days=i) for i in range(8)]
clinvar_week = [day.strftime('%b %-d') for day in clinvar_dates]    
print clinvar_week             
print "========= For Date :- %s =========" %asco_date 

'''########### ASCO ##########'''
    
def asco_update_checker(log_file): 
    diseases_update = {}
    log_file.write( '\n' )
    log_file.write( "========= ASCO ========= \n" )
    try:
        asco_pages = ['http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/assays-and-predictive-markers',
                      'http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/breast-cancer',
                      'http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/gastrointestinal-cancer',
                      'http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/genitourinary-cancer',
                      'http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/gynecologic-cancer',
                      'http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/head-and-neck-cancer',
                      'http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/hematologic-malignancies',
                      'http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/melanoma',
                      'https://www.asco.org/practice-guidelines/quality-guidelines/guidelines/thoracic-cancer',
                      'http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/neurooncology',
                      'http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/patient-and-survivor-care',
                      'http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/resource-stratified',
                      'http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/supportive-care-and-treatment-related-issues'
                      ]
                    
        for web_page in asco_pages:              
            page = requests.get(web_page)
            tree = html.fromstring(page.content)
            Disease = web_page.split('/')[-1]
            date_ext = tree.xpath('//span[@class="date-display-single"]/text()')
            diseases_update[Disease] = date_ext
            print Disease, date_ext
            Disease = ''; date_ext = []            
    except ConnectionError:
        time.sleep(15)
        log_file.write("*****Trying to connect to internet***** \n")
        asco_update_checker(log_file)
    else:
        log_file.write("1. Data collected from ASCO \n")
        #print diseases_update
        return diseases_update

def new_asco_update(diseases_updates,log_file):
    log_file.write("2. Checking updates for today \n")
    for disease in diseases_updates.keys():
        log_file.write("- For "+str(disease)+'\n')
        for update_date in diseases_updates[disease]:
            for check_date in asco_week: 
                #print "- For %s, checking for date %s" %(disease,check_date)
                if update_date == check_date:
                    message = " %s in ASCO has been updated on %s. Please check http://www.asco.org/practice-guidelines/quality-guidelines/guidelines/%s"%(disease,update_date, disease)
                    log_file.write("+ "+str(message)+'\n')
                    send_update(message, disease, update_date, log_file, website = 'ASCO')
                if update_date != check_date:
                    log_file.write(" -> No update on "+str(check_date)+", last update on "+str(update_date)+'\n')        
            

'''############ EMVclass #############'''

def EMVclass_update_checker(log_file):
    log_file.write( '\n' )
    log_file.write( "=============== EMVclass =============== \n" )
    log_file.write( "1. Checking Updates for EMVclass \n")
    current_length = os.path.getsize('./EMV_last_update/EmVClass.2017-Q2.csv')              
    
    try:
        webpage = 'http://www.egl-eurofins.com/emvclass/CSVArchives/EmVClass.2017-Q2.csv'
        response = urllib2.urlopen(webpage)
        if "Content-Length" in response.headers:
            updated_length = int(response.headers["Content-Length"])
        else:
            updated_length = len(response.read());
        return updated_length, current_length
    except ConnectionError:
        time.sleep(15)
        log_file.write( "****Trying to connect to internet***** \n")
        EMVclass_update_checker()

def new_EMVclass_update(updated_length, current_length, log_file):
    log_file.write('2. Checking the size of the CSV file \n')
    log_file.write( 'Previous size:- ' + str(current_length)+'\n') 
    log_file.write( 'Current size:- '+ str(updated_length) +'\n')
    message = 'New lines have been added on EMVclass and lines have increased from %d to %d ' %(current_length, updated_length)
    if updated_length != current_length:
        send_update(message, 'CSV', asco_date,log_file, 'EMVclass')
        log_file.write( "+ Updates from EMV class \n")    
    else:
        log_file.write( "No updates from EMV class \n")    


''' ################## Clinvar ################'''

def clinvar_update_checker(clinvar_date, log_file):
    log_file.write( "\n" )
    log_file.write( "========== Clinvar ============ \n" )
    log_file.write( '1. Checking updates for Clinvar \n' )
    #clinvar_date = 'Jun 1'
    try:
        flist=[]
        req = urllib2.Request('ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/')
        response = urllib2.urlopen(req)
        the_page = response.read()
        the_page = the_page.split('\r\n')
        temp_list = [i.split(' ') for i in the_page if i != '']
        for i in temp_list:
            for j in range(i.count('')):
                i.remove('')
            flist.append(i)
    except ConnectionError:
        log_file.write( " ***** Trying to connect to internet ***** \n" )
        time.sleep(15)
        clinvar_update_checker(log_file)
    else:        
        return flist
        
def new_clinvar_update(flist, clinvar_week, log_file):      
    the_entry =[]
    for i in flist:
        if i[-1] == 'xml':
            the_entry.append(i)      
    mnth, dy = the_entry[0][-4],the_entry[0][-3]
    update_date = mnth+' '+dy
    log_file.write("2. Data collected from Clinvar \n")
    for date in clinvar_week:
        log_file.write( 'Todays date:- '+str(date)+' Fetched date:- '+str(update_date)+'\n')
        if update_date == date:
            message = 'The xml sheet has been updated on %s'%(date)
            send_update(message,'XML', date, log_file, 'Clinvar')
            log_file.write(" + Update found for Clinvar \n")
        else: 
            log_file.write('No updates on '+str(date)+' from Clinvar \n')
            
'''############ Clinvitae #############'''

def Clinvitae_update_checker(log_file):
    log_file.write( '\n' )
    log_file.write( "=============== Clinvitae =============== \n" )
    log_file.write( "1. Checking Updates for Clinvitae \n")
    current_size = os.path.getsize('./clinvitae_last_update/clinvitae_download.zip') 
    
    try:
        webpage = 'http://s3-us-west-2.amazonaws.com/clinvitae/clinvitae_download.zip'
        response = urllib2.urlopen(webpage)
        if "Content-Length" in response.headers:
            update_size = int(response.headers["Content-Length"])
        else:
            update_size = len(response.read());
        return update_size, current_size
    except ConnectionError:
        time.sleep(15)
        log_file.write( "****Trying to connect to internet***** \n")
        Clinvitae_update_checker(log_file)

def new_Clinvitae_update(update_size, current_size, log_file):
    log_file.write('2. Checking the size of the ZIP files \n')
    log_file.write( 'Previous size:- ' + str(current_size)+'\n') 
    log_file.write( 'Current size:- '+ str(update_size) +'\n')
    message = 'Clinvitae has been updated and Size have increased from %d to %d ' %(current_size, update_size)
    if update_size != current_size:
        send_update(message, 'ZIP', asco_date,log_file, 'Clinvitae')
        log_file.write("+ Updates from Clinvitae \n")  
        download_update('http://s3-us-west-2.amazonaws.com/clinvitae/clinvitae_download.zip')
    else:
#        print current_size, update_size
        log_file.write( "No updates from Clinvitae \n")    
            

'''########### Common Function ##############'''

def send_update(message, disease, date, log_file, website):
    log_file.write( "3. Trying to send mail \n" )
    try:
        yag = yagmail.SMTP("updates.checking.bot@gmail.com", *********) #use your id and password incase
        TO = ["vinay@pieriandx.com"]
        Subject = "%s updated on %s by %s" %(disease, date, website)        
        for Recipient in TO:
            yag.send(TO, Subject, message)        
    except ConnectionError:
        time.sleep(15)
        send_update(message, disease, date,'')
    else:
        log_file.write("4. Mail has been sent to "+str(TO)+'\n')    

def log_file_generator(): # logging module
    logfile_name = asco_date+'_log'
    log_file = open('/home/test/Documents/Scripts_written_PDX/updatecheckr_ASCO_Clinvar_EMV/LOGS/'+logfile_name,'w')
    return log_file

def download_update(url):
    urllib.urlretrieve(url, url.split('/')[-1].split('.')[0])
    print "Download Complete!"
    
            
def main():
    log_file = log_file_generator()
    all_disease_updates = asco_update_checker(log_file)
    new_asco_update(all_disease_updates, log_file)
    
    updated_length, current_length = EMVclass_update_checker(log_file)
    new_EMVclass_update(updated_length, current_length, log_file) 
    
    flist = clinvar_update_checker(clinvar_date, log_file)
    new_clinvar_update(flist,clinvar_week, log_file)

    update_size, current_size = Clinvitae_update_checker(log_file)
    new_Clinvitae_update(update_size, current_size, log_file) 
    
main()
    
print '\n'
print "==========All Queries have ended=========="
print "\n"
            
