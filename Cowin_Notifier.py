#Defining APIs
import requests
from hashlib import sha256
import time
import json
import os
import playsound
import sys
import pandas as pd


def generate_otp(otp_request_header,generate_otp_url,validate_otp_url,secret):
    auth_token_check = input("Do you have an auth token? Yes/No: ")
    if str.lower(auth_token_check) == 'yes':
        auth_token = input("Please enter the auth token: ")
        return auth_token
    else:
        mobile_no = input("Please input mobile number : ")
        otp_gen_data = {"mobile":mobile_no,"secret":secret}
        TxnID_response = requests.post(generate_otp_url,json = otp_gen_data,headers = otp_request_header)
        if TxnID_response.status_code == 200:
            TxnID = TxnID_response.json()['txnId']
            one_time_pass = input("Please enter your one time password : ")
            otp_rec_data = {'otp': sha256(str(one_time_pass).encode('utf-8')).hexdigest(),"txnId" : TxnID}
            auth_token_resp = requests.post(validate_otp_url,json = otp_rec_data,headers = otp_request_header)
            if auth_token_resp.status_code == 200:
                auth_token = auth_token_resp.json()['token']
                print("Here is your auth token. Please save this and use it in future to save time! \n")
                print(auth_token)
                return auth_token


def get_availability_by_district(District_url,otp_request_header,district_id,date,vaccine,pin,age):
    attempt = 0
    while True:
        output_list = []
        time.sleep(5)
        attempt = attempt + 1
        print("\n\n\n Attempt : {}".format(attempt))
        district_resp = requests.get(District_url.format(district_id,date),headers = otp_request_header)
        if district_resp.status_code==200:
            try:
                district_resp = district_resp.json()
                for center in district_resp['centers']:
                    if center['sessions'][0]['available_capacity']>0:
                        output_list.append((center['center_id'],center['name'],center['block_name'],center['pincode'],center['fee_type'],center['sessions'][0]['available_capacity'],center['sessions'][0]['vaccine'],center['sessions'][0]['min_age_limit']))
                if output_list  != []:
                    check_preference(output_list,pin,vaccine,age)
            except Exception as e:
                print(e)
                print(district_resp)
        else:
            print("Received an error when trying to access availability. This is the error code: {}".format(district_resp.status_code))


def check_availability(District_url,otp_request_header):
    district_id = input("Please enter your district ID: ")
    district_id = int(district_id)
    date = input("Please enter the date from which you wish to check availability (DD-MM-YYYY) : ")
    vaccine = input("Are you looking for a particular vaccine? If yes, input Covaxin/Covishield, else input no : ")
    pin = input("Are you looking to look for a vaccine at a particular pin? Input pincode(eg.400001) if yes, else no : ")
    age = input("Are you looking to obtain the vaccine for a certain age group? Options : 18/45/no : ")
    get_availability_by_district(District_url,otp_request_header,district_id,date,vaccine,pin,age)

def check_preference(base_list,pin,vaccine,age):
    base_df = pd.DataFrame(base_list,columns=['Center_id','Name','Block','Pin','Fee','Slots','Vaccine','Age'])
    curr_dir = os.getcwd()
    output_df = pd.DataFrame()
    base_query = ''
    age_check = False
    vaccine_check = False
    pin_check = False
    if age != 'no':
        base_query = base_query + 'Age == "{}"'.format(age)
        age_check = True
    if vaccine != 'no':
        vaccine_check = True
        if age_check == True:
            base_query = base_query + 'and Vaccine == "{}"'.format(str.upper(vaccine))
        else:
            base_query = base_query + 'Vaccine == "{}"'.format(str.upper(vaccine))
    if pin != 'no':
        pin = int(pin)
        pin_list =[pin,pin+1,pin-1,pin+2,pin-2,pin+3,pin-3,pin+4,pin-4]
        if vaccine_check == True or age_check == True:
            for pin in pin_list:
                new_query = base_query
                new_query = new_query + 'and Pin == "{}"'.format(str(pin))
                output_df.append(base_df.query('{}'.format(new_query)))
        else:
            for pin in pin_list:
                new_query = base_query
                new_query = new_query + 'Pin =="{}"'.format(str(pin))
                output_df.append(base_df.query('{}'.format(new_query)))
    else:
        if vaccine_check == True or age_check == True:
            output_df.append(base_df.query('{}'.format(base_query)))    

        else:
            output_df = base_df
        if output_df.empty == False:
            playsound.playsound(curr_dir + '/Beep_Sound.wav')
            output_df.to_csv(curr_dir+'/Available_Slots.csv')
            sys.exit(0)
             
def main():
    generate_otp_url = 'https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP'
    validate_otp_url = 'https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp'
    District_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={}&date={}"
    secret = "U2FsdGVkX1/Bsqaq3UDufqnBrLxz251M+nFbTLQ510QratM3Lr7JF/HTtVupUoyD4gEKhO3k1eTjkKPO9klzvg=="
    otp_request_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    auth_token = generate_otp(otp_request_header,generate_otp_url,validate_otp_url,secret)
    otp_request_header['Authorization'] = "Bearer {}".format(auth_token)
    check_availability(District_url,otp_request_header)

if __name__ == '__main__':
    main()