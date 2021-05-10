#Defining APIs
import requests
from hashlib import sha256
import time
import json
import os
import playsound
import sys

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
        output_dict = {}
        time.sleep(5)
        attempt = attempt + 1
        print("\n\n\n Attempt : {}".format(attempt))
        district_resp = requests.get(District_url.format(district_id,date),headers = otp_request_header)
        if district_resp.status_code==200:
            district_resp = district_resp.json()
            for center in district_resp['centers']:
                if center['sessions'][0]['available_capacity']>0:
                    output_dict[center['center_id']] = {'Name':center['name'],'Block':center['block_name'],'PIN':center['pincode'],'Fee':center['fee_type'],'Slots':center['sessions'][0]['available_capacity'],'Vaccine':center['sessions'][0]['vaccine'],'Age':center['sessions'][0]['min_age_limit']}
            if output_dict  != {}:
                check_preference(output_dict,pin,vaccine,age)
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

def check_preference(available_dict,pin,vaccine,age):
    pin_updated = {}
    vaccine_out = {}
    final_out = {}
    condition_checker = False
    if str.lower(pin) != 'no':
        pin = int(pin)
        pin_list = [pin-5,pin-4,pin-3,pin-2,pin-1,pin,pin+1,pin+2,pin+3,pin+4,pin+5]
        for pins in pin_list:
            for k,v in available_dict.items():
                if pins == int(v['PIN']):
                    pin_updated[k] = available_dict[k]   
                    condition_checker = True      
    if str.lower(vaccine) != 'no':
        if pin_updated == {}:
            for k,v in available_dict.items():
                if str.upper(vaccine) == v['Vaccine']:
                    vaccine_out[k] = available_dict[k]
                    condition_checker = True
        else:    
            for k,v in pin_updated.items():
                if str.upper(vaccine) == v['Vaccine']:
                    vaccine_out[k] = available_dict[k]
                    condition_checker = True
    if str.lower(age) != 'no':
        age = int(age)
        if  vaccine_out != {}:
            for k,v in vaccine_out.items():
                if v['Age'] == age:
                    final_out[k] = vaccine_out[k]
                    condition_checker = True
        elif pin_updated != {}:
            for k,v in pin_updated.items():
                if v['Age'] == age:
                    final_out[k] = vaccine_out[k]
                    condition_checker = True
        else:
            for k,v in available_dict.items():
                if v['Age'] == age:
                    final_out[k] = available_dict[k]
                    condition_checker = True
    if condition_checker == True:
        if final_out != {}:
            print(final_out)
        elif vaccine_out != {}:
            print(vaccine_out)
        elif pin_updated != {}:
            print(pin_updated)
        curr_dir = os.getcwd()
        playsound.playsound(curr_dir + '/Beep_Sound.wav')
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