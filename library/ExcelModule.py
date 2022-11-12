#!/usr/bin/python
'''This program is to generate data files (VIP details,Vip Status, Profiles, Certificate and expiry data) captured from F5
and process it to generate final report''' 

from ansible.module_utils.basic import AnsibleModule
import pandas as pd
import numpy as np
import openpyxl

def main():
    result = dict(
    changed=True,
    original_message="",
    message="",
    )
    module = AnsibleModule(argument_spec={})
    
    #Reading Data Files    
    vip_prof1 = '/tmp/vip_profile1.csv'
    vip_prof2 = '/tmp/vip_profile2.csv'
    serverssl = '/tmp/serverssl.csv'
    clientssl = '/tmp/clientssl.csv'
    ssl_cert = '/tmp/ssl_certs.csv'
    expiredssl = '/tmp/expired.csv'
    
    #Processing Data Files    
    df_vip_prof1 = pd.read_csv(vip_prof1)
    df_vip_prof2 = pd.read_csv(vip_prof2)
    df_3 = pd.concat([df_vip_prof1,  df_vip_prof2],  ignore_index = True)    
    df_serverssl = pd.read_csv(serverssl)
    df_serverssl['Cert_Name'] = df_serverssl['Cert_Name'].str.replace("/Common/","")
    df_clientssl = pd.read_csv(clientssl)
    df_clientssl['Cert_Name'] = df_clientssl['Cert_Name'].str.replace("/Common/","")
    df_4 = pd.concat([df_serverssl,  df_clientssl],  ignore_index=True)
    merge_1 = pd.merge(df_3,  df_4,  on="Profile")
    df_ssl_cert = pd.read_csv(ssl_cert)
    merge_2 = pd.merge(merge_1,  df_ssl_cert,  on="Cert_Name")
    df_exp = pd.read_csv(expiredssl)
    df_exp['Cert_Name'] = df_exp['Cert_Name'].str.replace("/Common/","")
    
    #Converting CSV to XLSX and formatting columns    
    writer = pd.ExcelWriter('/tmp/Final.xlsx')
    merge_2.to_excel(writer, sheet_name='ssl_report', index=False, na_rep='NaN')
    df_exp.to_excel(writer, sheet_name='exp_cert_report', index=False, na_rep='NaN')    
    for column in merge_2:
        column_width = max(merge_2[column].astype(str).map(len).max(), len(column))
        col_idx = merge_2.columns.get_loc(column)
        writer.sheets['ssl_report'].set_column(col_idx, col_idx, column_width)
    for column in df_exp:
        column_width = max(df_exp[column].astype(str).map(len).max(), len(column))
        col_idx = df_exp.columns.get_loc(column)
        writer.sheets['exp_cert_report'].set_column(col_idx, col_idx, column_width)        
    
    writer.save()
    result["stdout_lines"] = { "message": "Report File Generated Successfully!!" }
    module.exit_json(changed=True, meta=result)

if __name__=="__main__":
    main()

 
