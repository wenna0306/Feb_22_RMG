import openpyxl
import pandas as pd
import plotly.graph_objects as go
import matplotlib
import numpy as np
import streamlit as st
from matplotlib.backends.backend_agg import RendererAgg
matplotlib.use('agg')
from st_btn_select import st_btn_select
import streamlit_authenticator as stauth
from wordcloud import WordCloud
_lock = RendererAgg.lock

# -----------------------------------------set page layout-------------------------------------------------------------
st.set_page_config(page_title='iSMM Dashboard',
                   page_icon = ':chart_with_upwards_trend:',
                   layout='wide',
                   initial_sidebar_state='collapsed')


#-----------------------------------------------User Authentication-----------------------------------------------
names = ['wenna', 'Lifei', 'Thiru', 'Mr.Loh']
usernames = ['wenna0306@gmail.com', 'Lifei', 'Thiru', 'booninn.loh@surbanajurong.com']
passwords = ['password', 'password', 'password', 'password']

hashed_passwords = stauth.hasher(passwords).generate()

authenticator = stauth.authenticate(names,usernames,hashed_passwords,
    'some_cookie_name','some_signature_key',cookie_expiry_days=30)

name, authentication_status = authenticator.login('Login','main')

if authentication_status:
    st.write('Welcome *%s*' % (name))


#======================================different pages setup=============================
    page = st_btn_select(('Faults', 'Schedules', 'Asset', 'Inventories'),
                        nav=True,
                        format_func=lambda name: name.capitalize(),
                        )

# =======================================Fault===================================================================
    if page =='Faults':
        html_card_title="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; padding-top: 5px; width: 600px;
           height: 50px;">
            <h1 class="card-title" style=color:#116a8c; font-family:Georgia; text-align: left; padding: 0px 0;">FAULT DASHBOARD</h1>
          </div>
        </div>
        """

        st.markdown(html_card_title, unsafe_allow_html=True)
        st.markdown('##')
        st.markdown('##')
        st.markdown(
            'Welcome to this Analysis App, get more detail from :point_right: [iSMM](https://ismm.sg/ce/login)')
        st.markdown('##')

        def fetch_file(filename):
            cols = ['Fault Number', 'Trade', 'Trade Category',
                    'Type of Fault', 'Impact', 'Site', 'Building', 'Floor', 'Room', 'Cancel Status', 'Reported Date',
                    'Fault Acknowledged Date', 'Responded on Site Date', 'RA Conducted Date',
                    'Work Started Date', 'Work Completed Date', 'Attended By', 'Action(s) Taken',
                    'Other Trades Required Date', 'Cost Cap Exceed Date',
                    'Assistance Requested Date', 'Fault Reference',
                     'Incident Report', 'Remarks']
            parse_dates = ['Reported Date',
                           'Fault Acknowledged Date', 'Responded on Site Date', 'RA Conducted Date',
                           'Work Started Date', 'Work Completed Date',
                           'Other Trades Required Date', 'Cost Cap Exceed Date',
                           'Assistance Requested Date']
            dtype_cols = {'Site': 'str', 'Building': 'str', 'Floor': 'str', 'Room': 'str'}
            return pd.read_excel(filename, header=1, index_col='Fault Number', usecols=cols, parse_dates=parse_dates, dtype=dtype_cols)


        df2 = fetch_file('Fault_RMG.xlsx')

        df2.columns = df2.columns.str.replace(' ', '_')
        df2['Time_Acknowledged_mins'] = (df2.Fault_Acknowledged_Date - df2.Reported_Date)/pd.Timedelta(minutes=1)
        df2['Time_Site_Reached_mins'] = (df2.Responded_on_Site_Date - df2.Reported_Date)/pd.Timedelta(minutes=1)
        df2['Time_Work_Started_mins'] = (df2.Work_Started_Date - df2.Reported_Date)/pd.Timedelta(minutes=1)
        df2['Time_Work_Recovered_mins'] = (df2.Work_Completed_Date - df2.Reported_Date)/pd.Timedelta(minutes=1)


        outstanding_cols = ['Trade', 'Trade_Category', 'Type_of_Fault', 'Impact', 'Site', 'Building', 'Floor', 'Room', 'Cancel_Status', 
        'Reported_Date', 'Other_Trades_Required_Date', 'Cost_Cap_Exceed_Date', 'Assistance_Requested_Date', 'Fault_Reference', 
         'Incident_Report', 'Remarks']
        df_outstanding = df2.loc[(df2['Cancel_Status'].isna()) & (df2['Work_Completed_Date'].isna()), outstanding_cols].copy()

        recovered_cols = ['Site', 'Building', 'Floor', 'Room', 'Trade', 'Trade_Category', 'Type_of_Fault', 'Time_Acknowledged_mins',
                   'Time_Site_Reached_mins', 'Time_Work_Started_mins', 'Time_Work_Recovered_mins']

        recovered_cols = ['Site', 'Building', 'Floor', 'Room', 'Trade', 'Trade_Category', 'Type_of_Fault', 'Attended_By', 'Remarks', 'Time_Acknowledged_mins',
                   'Time_Site_Reached_mins', 'Time_Work_Started_mins', 'Time_Work_Recovered_mins']

        df3 = df2.loc[(df2['Cancel_Status'].isna()) & (df2['Work_Completed_Date'].notna()),recovered_cols].copy()  # recovered Fault

        df_daily = df2.loc[(df2['Cancel_Status'].isna()) & (df2['Work_Completed_Date'].notna()),:].copy()


        # df_low = df3[df3.Remarks.str.contains('low|Low|LOW|NA|NaN')]
        # df_medium = df3[df3.Remarks.str.contains('medium|Medium|MEDIUM')]
        # df_high = df3[df3.Remarks.str.contains('high|High|HIGH')]

        df_high = df3[df3.Remarks.str.contains('high|High|HIGH')].copy()
        df_medium = df3[df3.Remarks.str.contains('medium|Medium|MEDIUM')].copy()
        df_low = df3[~df3.Remarks.str.contains('medium|Medium|MEDIUM|high|High|HIGH')].copy()
        

        bin_responded_low = [0, 15, np.inf]
        label_responded_low = ['0-15mins', '15-np.inf']

        bin_recovered_low = [0, 1440, np.inf]
        label_recovered_low = ['0-24hr', '24-np.inf']

        bin_responded_medium = [0, 10, np.inf]
        label_responded_medium = ['0-10mins', '10-np.inf']

        bin_recovered_medium = [0, 60, np.inf]
        label_recovered_medium = ['0-1hr', '1-np.inf']

        # bin_responded_high = [0, 5, np.inf]
        # label_responded_high = ['0-5mins', '5-np.inf']

        bin_responded_high = [0, np.inf]
        label_responded_high = ['0-np.inf']

        bin_recovered_high = [0, 30, np.inf]
        label_recovered_high = ['0-0.5hr', '0.5-np.inf']

        df_low['KPI_For_Responded'] = pd.cut(df_low.Time_Site_Reached_mins, bins=bin_responded_low, labels=label_responded_low, include_lowest=True)
        df_low['KPI_For_Recovered'] = pd.cut(df_low.Time_Work_Recovered_mins, bins=bin_recovered_low, labels=label_recovered_low, include_lowest=True)

        df_medium['KPI_For_Responded'] = pd.cut(df_medium.Time_Site_Reached_mins, bins=bin_responded_medium, labels=label_responded_medium, include_lowest=True)
        df_medium['KPI_For_Recovered'] = pd.cut(df_medium.Time_Work_Recovered_mins, bins=bin_recovered_medium, labels=label_recovered_medium, include_lowest=True)

        df_high['KPI_For_Responded'] = pd.cut(df_high.Time_Site_Reached_mins, bins=bin_responded_high, labels=label_responded_high, include_lowest=True)
        df_high['KPI_For_Recovered'] = pd.cut(df_high.Time_Work_Recovered_mins, bins=bin_recovered_high, labels=label_recovered_high, include_lowest=True)

        # ----------------------------------------Sidebar---------------------------------------------------------------------
        st.sidebar.header('Please Filter Here:')

        Trade = st.sidebar.multiselect(
            'Select the Trade:',
            options=df2['Trade'].unique(),
            default=df2['Trade'].unique()
        )
        # st.sidebar.markdown('---')
        Trade_Category = st.sidebar.multiselect(
            'Select the Trade Category:',
            options=df2['Trade_Category'].unique(),
            default=df2['Trade_Category'].unique()
        )

        df2 = df2.query(
            'Trade ==@Trade & Trade_Category==@Trade_Category'
            )


        # ----------------------------------------------Main Page--------------------------------------------------------
        html_card_subheader_outstanding="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 350px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Outstanding Fault</h3>
          </div>
        </div>
        """
        html_card_subheader_daily="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 350px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Daily Fault Cases</h3>
          </div>
        </div>
        """
        html_card_subheader_KPI_Responded="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 450px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">KPI Monitoring-Responded</h3>
          </div>
        </div>
        """
        html_card_subheader_KPI_Recovered="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 450px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">KPI Monitoring-Recovered</h3>
          </div>
        </div>
        """
        html_card_subheader_Tier1="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 400px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Recovered Fault vs Trade</h3>
          </div>
        </div>
        """
        html_card_subheader_Tier2="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 520px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Recovered Fault vs Trade Category</h3>
          </div>
        </div>
        """
        html_card_subheader_Tier3="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 500px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Recovered Fault vs Type of Fault</h3>
          </div>
        </div>
        """
        html_card_subheader_location="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 450px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Recovered Fault vs Location</h3>
          </div>
        </div>
        """
        html_card_subheader_fault_Technician="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 550px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">No. of Recovered Fault vs Technician</h3>
          </div>
        </div>
        """
    # -----------------------------------------------------Fault Summary--------------------------------------------
        total_fault = df2.shape[0]
        fault_cancelled = int(df2['Cancel_Status'].notna().sum())
        fault_not_recovered = df2.loc[(df2['Cancel_Status'].isna()) & (df2['Work_Completed_Date'].isna()),:].shape[0]
        fault_recovered = df2.loc[(df2['Cancel_Status'].isna()) & (df2['Work_Completed_Date'].notna()),:].shape[0]
        fault_incident = int(df2['Incident_Report'].sum())

        fault_high = df3[df3.Remarks.str.contains('high|High|HIGH')].shape[0]
        fault_medium = df3[df3.Remarks.str.contains('medium|Medium|MEDIUM')].shape[0]
        fault_low = df3[~df3.Remarks.str.contains('medium|Medium|MEDIUM|high|High|HIGH')].shape[0]


        column01_fault, column02_fault, column03_fault, column04_fault, column05_fault = st.columns(5)
        with column01_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Total</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{total_fault}</h2>", unsafe_allow_html=True)

        with column02_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Cancelled</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{fault_cancelled}</h2>", unsafe_allow_html=True)

        with column03_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Outstanding</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: red;'>{fault_not_recovered}</h2>", unsafe_allow_html=True)

        with column04_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Recovered</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{fault_recovered}</h2>", unsafe_allow_html=True)

        with column05_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Incident Report</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: red;'>{fault_incident}</h2>", unsafe_allow_html=True)

        st.markdown('##')
        st.markdown('##')
        st.markdown('##')
        column06_fault, column07_fault, column08_fault, column09_fault, column10_fault = st.columns(5)
        with column06_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Low</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{fault_low}</h2>", unsafe_allow_html=True)

        with column07_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Medium</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{fault_medium}</h2>", unsafe_allow_html=True)

        with column08_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>High</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{fault_high}</h2>", unsafe_allow_html=True)

        with column09_fault, _lock:
            st.markdown('')

        with column10_fault, _lock:
            st.markdown('')
        
    #--------------------------------------- color & width & opacity-------------------------------------------------
        # all chart
        titlefontcolor = '#116a8c'

        # pie chart for outstanding and tier1
        colorpieoutstanding = ['#116a8c', '#4c9085', '#50a747', '#59656d', '#06c2ac', '#137e6d', '#929906', '#ff9408']
        colorpierecoveredtier1 = ['#116a8c', '#4c9085', '#50a747', '#59656d', '#06c2ac', '#137e6d', '#929906', '#ff9408']

        # all barchart include stack bar chart and individual barchart and linechart
        plot_bgcolor = 'rgba(0,0,0,0)'
        gridwidth = 0.1
        gridcolor = '#1f3b4d'

        # stack barchart
        colorstackbarpass = '#116a8c'
        colorstackbarfail = '#ffdb58'

        # individual barchart color, barline color& width, bar opacity
        markercolor = '#116a8c'
        markerlinecolor = '#116a8c'
        markerlinewidth = 1
        opacity01 = 1
        opacity02 = 1
        opacity03 = 1

        # x&y axis width and color
        linewidth_xy_axis = 1
        linecolor_xy_axis = '#59656d'

        # linechart
        linecolor = '#96ae8d'
        linewidth = 2

    #---------------------------------------Outstanding Faults-----------------------------------------------------
        st.markdown('##')
        st.markdown('##')
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
        # st.markdown(':wavy_dash:' *50)
        # st.markdown('---')
        st.markdown(html_card_subheader_outstanding, unsafe_allow_html=True)
        st.markdown('##')

        df_outstanding_show = df_outstanding.loc[:, ['Trade', 'Trade_Category', 'Type_of_Fault', 'Site', 'Building', 'Floor', 'Room',
                                                     'Reported_Date', 'Other_Trades_Required_Date', 'Cost_Cap_Exceed_Date', 'Assistance_Requested_Date',
                                                    'Remarks']].sort_values('Trade')

        props = 'font-style: italic; color: #ffffff; font-size:0.8em; font-weight:normal;'  #border: 0.0001px solid #116a8c; background: #116a8c'
        df_outstandingdataframe = df_outstanding_show.style.applymap(lambda x: props)
        st.dataframe(df_outstandingdataframe, 2000, 200)

        ser_outstanding_building = df_outstanding.groupby(['Trade'])['Type_of_Fault'].count().sort_values(ascending=False)
        ser_outstanding_category = df_outstanding.groupby(['Trade_Category'])['Type_of_Fault'].count().sort_values(ascending=False)

        x_outstanding_building = ser_outstanding_building.index
        y_outstanding_building = ser_outstanding_building.values
        x_outstanding_category = ser_outstanding_category.index
        y_outstanding_category = ser_outstanding_category.values

        fig_outstanding_building, fig_outstanding_category = st.columns([1, 2])

        with fig_outstanding_building, _lock:
            fig_outstanding_building = go.Figure(data=[go.Pie(labels=x_outstanding_building, values=y_outstanding_building,
                                                              hoverinfo='all', textinfo='label+percent+value', textfont_size=15,
                                                              textfont_color='white', textposition='inside', showlegend=False,
                                                              hole=.4)])
            fig_outstanding_building.update_layout(title='Number of Fault vs Trade', annotations=[dict(text='Outstanding', x=0.5, y=0.5, font_color='white', font_size=15, showarrow=False)])
            fig_outstanding_building.update_traces(marker=dict(colors=colorpieoutstanding))
            st.plotly_chart(fig_outstanding_building, use_container_width=True)

        with fig_outstanding_category, _lock:
            fig_outstanding_category = go.Figure(data=[go.Bar(x=x_outstanding_category, y=y_outstanding_category, orientation='v',
                                                              text=y_outstanding_category, textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                                               textposition='auto', textangle=-45)])
            fig_outstanding_category.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_outstanding_category.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_outstanding_category.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth)
            fig_outstanding_category.update_layout(title='Number of Fault vs Trade Category', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig_outstanding_category, use_container_width=True)



        Abala = df_outstanding[df_outstanding.Remarks.str.contains('abala|Abala|A.bala|a.bala|A.Bala')].shape[0]
        Allan = df_outstanding[df_outstanding.Remarks.str.contains('Allan|allan|allen|Allen|alan|alen')].shape[0]
        Aru = df_outstanding[df_outstanding.Remarks.str.contains('Aru|aru')].shape[0]
        Hossain = df_outstanding[df_outstanding.Remarks.str.contains('Hossain|hossain')].shape[0]
        Ilayaraja = df_outstanding[df_outstanding.Remarks.str.contains('Ilayaraja|ilayaraja')].shape[0]
        Isyamudin = df_outstanding[df_outstanding.Remarks.str.contains('Isyamudin|isyamudin|lsyamudin|Lsyamudin')].shape[0]
        Lifei = df_outstanding[df_outstanding.Remarks.str.contains('Lifei|lifei|Li Fei|Li fei|li fei')].shape[0]
        Mani = df_outstanding[df_outstanding.Remarks.str.contains('Mani|mani')].shape[0]
        Mingcai = df_outstanding[df_outstanding.Remarks.str.contains('Mingcai|mingcai|Ming Cai|Ming cai|ming cai')].shape[0]
        Nazri = df_outstanding[df_outstanding.Remarks.str.contains('Nazri|nazri')].shape[0]
        Satha = df_outstanding[df_outstanding.Remarks.str.contains('Satha|satha')].shape[0]
        Senthil = df_outstanding[df_outstanding.Remarks.str.contains('Senthil|senthil')].shape[0]
        Shanmu = df_outstanding[df_outstanding.Remarks.str.contains('Shanmu|shanmu')].shape[0]
        Su = df_outstanding[df_outstanding.Remarks.str.contains('-Su|-su|- Su|- su')].shape[0]
        Vbala = df_outstanding[df_outstanding.Remarks.str.contains('Vbala|vbala|V.bala|v.bala|V.Bala')].shape[0]
        Jailani = df_outstanding[df_outstanding.Remarks.str.contains('Jailani|jailani|Jailan|jailan|Jailan|jailan')].shape[0]
        Packiyaraj = df_outstanding[df_outstanding.Remarks.str.contains('Packiyaraj|packiyaraj')].shape[0]
        Ela = df_outstanding[df_outstanding.Remarks.str.contains('Ela|ela')].shape[0]
        FRC = df_outstanding[df_outstanding.Remarks.str.contains('FRC|frc|Frc')].shape[0]
        Thandapani = df_outstanding[df_outstanding.Remarks.str.contains('Thandapani|thandapani')].shape[0]
        Gary = df_outstanding[df_outstanding.Remarks.str.contains('Gary|gary')].shape[0]
        Murugan = df_outstanding[df_outstanding.Remarks.str.contains('Murugan|murugan')].shape[0]
        Rabart = df_outstanding[df_outstanding.Remarks.str.contains('Rabart|rabart')].shape[0]
        Dutytech = df_outstanding[df_outstanding.Remarks.str.contains('Dutytech|dutytech')].shape[0]

    


        x_people_outstanding = ['Abala', 'Allan', 'Aru', 'Hossain', 'Ilayaraja', 'Isyamudin', 'LiFei', 'Mani', 'Mingcai', 'Nazri', 'Satha', 'Senthil', 'Shanmu', 'Su', 'Vbala', 'Jailani', 'Packiyaraj', 'Ela', 'FRC', 'Thandapani', 'Gary', 'Murugan', 'Rabart', 'Dutytech']
        y_people_outstanding = [Abala, Allan, Aru, Hossain, Ilayaraja, Isyamudin, Lifei, Mani, Mingcai, Nazri, Satha, Senthil, Shanmu, Su, Vbala, Jailani, Packiyaraj, Ela, FRC, Thandapani, Gary, Murugan, Rabart, Dutytech]

        y_people_outstanding_sum = sum(y_people_outstanding)
        st.markdown(f"Total outstanding Fault = {y_people_outstanding_sum}")

        fig_outstanding_technician, fig_outstanding_empty = st.columns(2)
        with fig_outstanding_technician, _lock:

            fig_outstanding_technician = go.Figure(data=[go.Bar(x=x_people_outstanding, y=y_people_outstanding, orientation='v', text=y_people_outstanding,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45)])
            fig_outstanding_technician.update_xaxes(title_text="Name", title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                                gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickangle=-45)
            fig_outstanding_technician.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=False,
                                gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_outstanding_technician.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig_outstanding_technician.update_layout(title='Number of Fault vs Name', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig_outstanding_technician, use_container_width=True)

        with fig_outstanding_empty, _lock:
            st.empty()



    #--------------------------------------Daily Fault----------------------------------------------------------
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
        st.markdown(html_card_subheader_daily, unsafe_allow_html=True)
        st.markdown('##')


        x_daily = df_daily['Reported_Date'].dt.day.value_counts().sort_index().index
        y_daily = df_daily['Reported_Date'].dt.day.value_counts().sort_index().values
        y_mean = df_daily['Reported_Date'].dt.day.value_counts().sort_index().mean()

        day_max = df_daily.Reported_Date.dt.day.max()

        fig_daily = go.Figure(data=go.Scatter(x=x_daily, y=y_daily, mode='lines+markers+text', line=dict(color='#116a8c', width=3),
                                              text=y_daily, textfont=dict(family='sana serif', size=14, color='#c4fff7'), textposition='top center'))
        fig_daily.add_hline(y=y_mean, line_dash='dot', line_color=linecolor, line_width=linewidth, annotation_text='Average Line',
                                  annotation_position='bottom right', annotation_font_size=18, annotation_font_color='green')
        fig_daily.update_xaxes(title_text='Date', tickangle=-45, title_font_color=titlefontcolor, tickmode='linear', range=[1, day_max],
                                           showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, zeroline=False)
        fig_daily.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=False,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, zeroline=False)
        fig_daily.update_layout(title='Number of Fault vs Date', plot_bgcolor=plot_bgcolor)
        st.plotly_chart(fig_daily, use_container_width=True)


    #---------------------------------------------KPI Monitoring-------------------------------------------------------
        st.markdown('##')
        st.markdown(html_card_subheader_KPI_Responded, unsafe_allow_html=True)
        st.markdown('##')
        st.markdown('Response Time refers to the time the fault or emergency was reported to the time the Contractor arrived on-site with evidence', )
        st.markdown('##')


    ## Low Faults
        x_KPI_building_015_Responded = df_low.groupby(by='KPI_For_Responded').Trade.value_counts().loc['0-15mins'].index
        x_KPI_building_15inf_Responded = df_low.groupby(by='KPI_For_Responded').Trade.value_counts().loc['15-np.inf'].index

        y_KPI_building_015_Responded = df_low.groupby(by='KPI_For_Responded').Trade.value_counts().loc['0-15mins'].values
        y_KPI_building_15inf_Responded = df_low.groupby(by='KPI_For_Responded').Trade.value_counts().loc['15-np.inf'].values

        x_KPI_category_015_Responded = df_low.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['0-15mins'].index
        x_KPI_category_15inf_Responded = df_low.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['15-np.inf'].index

        y_KPI_category_015_Responded = df_low.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['0-15mins'].values
        y_KPI_category_15inf_Responded = df_low.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['15-np.inf'].values

        fig_responded_building_low, fig_responded_category_low = st.columns([1, 2])
        with fig_responded_building_low, _lock:
            fig_responded_building_low = go.Figure(data=[
                go.Bar(name='0-15mins', x=x_KPI_building_015_Responded, y=y_KPI_building_015_Responded, marker_color=colorstackbarpass),
                go.Bar(name='>15mins', x=x_KPI_building_15inf_Responded, y=y_KPI_building_15inf_Responded, marker_color=colorstackbarfail)
            ])
            fig_responded_building_low.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolor,
                                                    showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_building_low.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True,
                                                    gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_building_low.update_layout(barmode='stack', title='KPI_Low vs Trade',
                                                     plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig_responded_building_low, use_container_width=True)

        with fig_responded_category_low, _lock:
            fig_responded_category_low = go.Figure(data=[
                go.Bar(name='0-15mins', x=x_KPI_category_015_Responded, y=y_KPI_category_015_Responded, marker_color=colorstackbarpass),
                go.Bar(name='>15mins', x=x_KPI_category_15inf_Responded, y=y_KPI_category_15inf_Responded, marker_color=colorstackbarfail),
            ])
            fig_responded_category_low.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor,
                                                showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_category_low.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True,
                                                    gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_category_low.update_layout(barmode='stack', title='KPI_Low vs Trade Category', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig_responded_category_low, use_container_width=True)

    ## Medium Faults
        fig_responded_building_medium, fig_responded_category_medium, fig_space_responded, fig_responded_building_high, fig_responded_category_high= st.columns([1, 1, 0.5, 1, 1])

        x_KPI_building_010_Responded = df_medium.groupby(by='KPI_For_Responded').Trade.value_counts().loc['0-10mins'].index
        x_KPI_building_10inf_Responded = df_medium.groupby(by='KPI_For_Responded').Trade.value_counts().loc['10-np.inf'].index

        y_KPI_building_010_Responded = df_medium.groupby(by='KPI_For_Responded').Trade.value_counts().loc['0-10mins'].values
        y_KPI_building_10inf_Responded = df_medium.groupby(by='KPI_For_Responded').Trade.value_counts().loc['10-np.inf'].values

        x_KPI_category_010_Responded = df_medium.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['0-10mins'].index
        x_KPI_category_10inf_Responded = df_medium.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['10-np.inf'].index

        y_KPI_category_010_Responded = df_medium.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['0-10mins'].values
        y_KPI_category_10inf_Responded = df_medium.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['10-np.inf'].values

        with fig_responded_building_medium, _lock:
            fig_responded_building_medium = go.Figure(data=[
                go.Bar(name='0-10mins', x=x_KPI_building_010_Responded, y=y_KPI_building_010_Responded, marker_color=colorstackbarpass),
                go.Bar(name='>10mins', x=x_KPI_building_10inf_Responded, y=y_KPI_building_10inf_Responded, marker_color=colorstackbarfail)
            ])
            fig_responded_building_medium.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolor,
                                                    showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_building_medium.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True,
                                                       gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_building_medium.update_layout(barmode='stack', title='KPI_Medium vs Trade', plot_bgcolor=plot_bgcolor, height=300)
            st.plotly_chart(fig_responded_building_medium, use_container_width=True)

        with fig_responded_category_medium, _lock:
            fig_responded_category_medium = go.Figure(data=[
                go.Bar(name='0-10mins', x=x_KPI_category_010_Responded, y=y_KPI_category_010_Responded, marker_color=colorstackbarpass),
                go.Bar(name='>10mins', x=x_KPI_category_10inf_Responded, y=y_KPI_category_10inf_Responded, marker_color=colorstackbarfail),
            ])
            fig_responded_category_medium.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor,
                                                showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_category_medium.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True,
                                                       gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_category_medium.update_layout(barmode='stack', title='KPI_Medium vs Trade Category',
                                                 plot_bgcolor=plot_bgcolor, height=300)
            st.plotly_chart(fig_responded_category_medium, use_container_width=True)

            with fig_space_responded, _lock:
                st.empty()

    ## High Faults
            # x_KPI_building_05_Responded = df_high.groupby(by='KPI_For_Responded').Trade.value_counts().loc['0-5mins'].index
            # x_KPI_building_5inf_Responded = df_high.groupby(by='KPI_For_Responded').Trade.value_counts().loc['5-np.inf'].index

            # y_KPI_building_05_Responded = df_high.groupby(by='KPI_For_Responded').Trade.value_counts().loc['0-5mins'].values
            # y_KPI_building_5inf_Responded = df_high.groupby(by='KPI_For_Responded').Trade.value_counts().loc['5-np.inf'].values

            # x_KPI_category_05_Responded = df_high.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['0-5mins'].index
            # x_KPI_category_5inf_Responded = df_high.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['5-np.inf'].index

            # y_KPI_category_05_Responded = df_high.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['0-5mins'].values
            # y_KPI_category_5inf_Responded = df_high.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['5-np.inf'].values

## there is no 0-5mins response for high fault !!!!!!


            x_KPI_building_5inf_Responded = df_high.groupby(by='KPI_For_Responded').Trade.value_counts().loc['0-np.inf'].index

            y_KPI_building_5inf_Responded = df_high.groupby(by='KPI_For_Responded').Trade.value_counts().loc['0-np.inf'].values

            x_KPI_category_5inf_Responded = df_high.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['0-np.inf'].index

            y_KPI_category_5inf_Responded = df_high.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['0-np.inf'].values

        with fig_responded_building_high, _lock:
            fig_responded_building_high= go.Figure(data=[
                # go.Bar(name='0-5mins', x=x_KPI_building_05_Responded, y=y_KPI_building_05_Responded, marker_color=colorstackbarpass),
                go.Bar(name='>5mins', x=x_KPI_building_5inf_Responded, y=y_KPI_building_5inf_Responded, marker_color=colorstackbarfail)
            ])
            fig_responded_building_high.update_xaxes(title_text="Trade", tickangle=-45,title_font_color=titlefontcolor,
                                                     showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True,linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_building_high.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor,showgrid=True,
                                                     gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_building_high.update_layout(barmode='stack', title='KPI_High vs Trade', plot_bgcolor=plot_bgcolor, height=300)
            st.plotly_chart(fig_responded_building_high, use_container_width=True)

        with fig_responded_category_high, _lock:
            fig_responded_category_high = go.Figure(data=[
                # go.Bar(name='0-5mins', x=x_KPI_category_05_Responded, y=y_KPI_category_05_Responded, marker_color=colorstackbarpass),
                go.Bar(name='>5mins', x=x_KPI_category_5inf_Responded, y=y_KPI_category_5inf_Responded, marker_color=colorstackbarfail),
            ])
            fig_responded_category_high.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor,
                                                    showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_category_high.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor,
                                                    showgrid=True, gridwidth=gridwidth, gridcolor=gridcolor, showline=True,
                                                     linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_category_high.update_layout(barmode='stack', title='KPI_High vs Trade Category', plot_bgcolor=plot_bgcolor, height=300)
            st.plotly_chart(fig_responded_category_high, use_container_width=True)


        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_KPI_Recovered, unsafe_allow_html=True)
        st.markdown('##')
        st.markdown('Recovery Time refers to the time the fault or emergency was reported to the time the Contractor completed the work with evidence')
        st.markdown('##')

    ## Low Faults
        x_KPI_building_024_Recovered = df_low.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['0-24hr'].index
        x_KPI_building_24inf_Recovered = df_low.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['24-np.inf'].index

        y_KPI_building_024_Recovered = df_low.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['0-24hr'].values
        y_KPI_building_24inf_Recovered = df_low.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['24-np.inf'].values

        x_KPI_category_024_Recovered = df_low.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['0-24hr'].index
        x_KPI_category_24inf_Recovered = df_low.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['24-np.inf'].index

        y_KPI_category_024_Recovered = df_low.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['0-24hr'].values
        y_KPI_category_24inf_Recovered = df_low.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['24-np.inf'].values

        fig_recovered_building_low, fig_recovered_category_low = st.columns([1, 2])
        with fig_recovered_building_low, _lock:
            fig_recovered_building_low = go.Figure(data=[
                go.Bar(name='0-24hrs', x=x_KPI_building_024_Recovered, y=y_KPI_building_024_Recovered, marker_color=colorstackbarpass),
                go.Bar(name='>24hrs', x=x_KPI_building_24inf_Recovered, y=y_KPI_building_24inf_Recovered, marker_color=colorstackbarfail)
            ])
            fig_recovered_building_low.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolor,
                                                    showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_building_low.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True,
                                                    gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_building_low.update_layout(barmode='stack', title='KPI_Low vs Trade', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig_recovered_building_low, use_container_width=True)

        with fig_recovered_category_low, _lock:
            fig_recovered_category_low = go.Figure(data=[
                go.Bar(name='0-24hrs', x=x_KPI_category_024_Recovered, y=y_KPI_category_024_Recovered, marker_color=colorstackbarpass),
                go.Bar(name='>24hrs', x=x_KPI_category_24inf_Recovered, y=y_KPI_category_24inf_Recovered, marker_color=colorstackbarfail)
            ])
            fig_recovered_category_low.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor,
                                                    showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_category_low.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True,
                                                    gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_category_low.update_layout(barmode='stack', title='KPI_Low vs Trade Category', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig_recovered_category_low, use_container_width=True)

     ## Medium Faults
        fig_recovered_building_medium, fig_recovered_category_medium, fig_space_recovered, fig_recovered_building_high, fig_recovered_category_high = st.columns([1, 1, 0.5, 1, 1])

        x_KPI_building_01_Recovered = df_medium.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['0-1hr'].index
        x_KPI_building_1inf_Recovered = df_medium.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['1-np.inf'].index

        y_KPI_building_01_Recovered = df_medium.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['0-1hr'].values
        y_KPI_building_1inf_Recovered = df_medium.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['1-np.inf'].values

        x_KPI_category_01_Recovered = df_medium.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['0-1hr'].index
        x_KPI_category_1inf_Recovered = df_medium.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['1-np.inf'].index

        y_KPI_category_01_Recovered = df_medium.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['0-1hr'].values
        y_KPI_category_1inf_Recovered = df_medium.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['1-np.inf'].values

        with fig_recovered_building_medium, _lock:
            fig_recovered_building_medium = go.Figure(data=[
                go.Bar(name='0-1hr', x=x_KPI_building_01_Recovered, y=y_KPI_building_01_Recovered, marker_color=colorstackbarpass),
                go.Bar(name='>1hrs', x=x_KPI_building_1inf_Recovered, y=y_KPI_building_1inf_Recovered, marker_color=colorstackbarfail)
            ])
            fig_recovered_building_medium.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolor,
                                                       showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_building_medium.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True,
                                                       gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_building_medium.update_layout(barmode='stack', title='KPI_Medium vs Trade',
                                                        plot_bgcolor=plot_bgcolor, height=300)
            st.plotly_chart(fig_recovered_building_medium, use_container_width=True)

        with fig_recovered_category_medium, _lock:
            fig_recovered_category_medium = go.Figure(data=[
                go.Bar(name='0-1hr', x=x_KPI_category_01_Recovered, y=y_KPI_category_01_Recovered, marker_color=colorstackbarpass),
                go.Bar(name='>1hrs', x=x_KPI_category_1inf_Recovered, y=y_KPI_category_1inf_Recovered, marker_color=colorstackbarfail),
            ])
            fig_recovered_category_medium.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor,
                                                       showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_category_medium.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True,
                                                       gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_category_medium.update_layout(barmode='stack', title='KPI_Medium vs Trade Category',
                                                        plot_bgcolor=plot_bgcolor, height=300)
            st.plotly_chart(fig_recovered_category_medium, use_container_width=True)

        with fig_space_recovered, _lock:
            st.empty()

    ## High Faults
        x_KPI_building_005_Recovered = df_high.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['0-0.5hr'].index
        x_KPI_building_05inf_Recovered = df_high.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['0.5-np.inf'].index

        y_KPI_building_005_Recovered = df_high.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['0-0.5hr'].values
        y_KPI_building_05inf_Recovered = df_high.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['0.5-np.inf'].values

        x_KPI_category_005_Recovered = df_high.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['0-0.5hr'].index
        x_KPI_category_05inf_Recovered = df_high.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['0.5-np.inf'].index

        y_KPI_category_005_Recovered = df_high.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['0-0.5hr'].values
        y_KPI_category_05inf_Recovered = df_high.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['0.5-np.inf'].values

        with fig_recovered_building_high, _lock:
            fig_recovered_building_high = go.Figure(data=[
                go.Bar(name='0-0.5hr', x=x_KPI_building_005_Recovered, y=y_KPI_building_005_Recovered, marker_color=colorstackbarpass),
                go.Bar(name='>0.5hr', x=x_KPI_building_05inf_Recovered, y=y_KPI_building_05inf_Recovered, marker_color=colorstackbarfail)
            ])
            fig_recovered_building_high.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolor,
                                                       showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_building_high.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True,
                                                     gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_building_high.update_layout(barmode='stack', title='KPI_High vs Trade', plot_bgcolor=plot_bgcolor, height=300)
            st.plotly_chart(fig_recovered_building_high, use_container_width=True)

        with fig_recovered_category_high, _lock:
            fig_recovered_category_high = go.Figure(data=[
                go.Bar(name='0-0.5hr', x=x_KPI_category_005_Recovered, y=y_KPI_category_005_Recovered, marker_color=colorstackbarpass),
                go.Bar(name='>0.5hr', x=x_KPI_category_05inf_Recovered, y=y_KPI_category_05inf_Recovered, marker_color=colorstackbarfail),
                ])
            fig_recovered_category_high.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor,
                                                       showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_category_high.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor,showgrid=True,
                                                     gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_category_high.update_layout(barmode='stack', title='KPI_High vs Trade Category', plot_bgcolor=plot_bgcolor, height=300)
            st.plotly_chart(fig_recovered_category_high, use_container_width=True)


 #---------------------------Fault vs Trade & Trade Category & Type of Fault----------------------------------
        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_Tier1, unsafe_allow_html=True)
        st.markdown('##')


        df3['Time_Acknowledged_hrs'] = df3.Time_Acknowledged_mins/60
        df3['Time_Site_Reached_hrs'] = df3.Time_Site_Reached_mins/60
        df3['Time_Work_Started_hrs'] = df3.Time_Work_Started_mins/60
        df3['Time_Work_Recovered_hrs'] = df3.Time_Work_Recovered_mins/60

        df4 = df3.loc[:, ['Site', 'Building', 'Floor', 'Room', 'Trade', 'Trade_Category', 'Type_of_Fault',
                          'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']].copy()
        df4= df4[['Site', 'Building', 'Floor', 'Room', 'Trade', 'Trade_Category', 'Type_of_Fault', 'Time_Acknowledged_hrs',
                  'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']]

        grouptrade_usecols = ['Trade', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']

        df5 = df4[grouptrade_usecols].groupby(by=['Trade']).agg(['count', 'max', 'min', 'mean', 'sum']).sort_values((     'Time_Acknowledged_hrs', 'count'), ascending=False)
        cols_name = ['Fault_Acknowledged_count', 'Fault_Acknowledged_max(hrs)', 'Fault_Acknowledged_min(hrs)', 'Fault_Acknowledged_mean(hrs)',
                       'Fault_Acknowledged_sum(hrs)', 'Fault_Site_Reached_count', 'Fault_Site_Reached_max(hrs)', 'Fault_Site_Reached_min(hrs)',
                       'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)', 'Fault_Work_Started_count', 'Fault_Work_Started_max(hrs)',
                       'Fault_Work_Started_min(hrs)', 'Fault_Work_Started_mean(hrs)', 'Fault_Work_Started_sum(hrs)', 'Fault_Recovered_count',
                       'Fault_Recovered_max(hrs)', 'Fault_Recovered_min(hrs)', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']
        df5.columns = cols_name
        df6 = df5.loc[:, ['Fault_Site_Reached_count', 'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)',
                      'Fault_Recovered_count', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']].copy()
        df6.reset_index(inplace=True)

        x = df6['Trade']
        y4 = df6.Fault_Recovered_count
        y5 = df6['Fault_Recovered_mean(hrs)']
        y6 = df6['Fault_Recovered_sum(hrs)']

        fig04, fig05, fig06 = st.columns(3)
        with fig04, _lock:
            fig04 = go.Figure(data=[go.Pie(values=y4, labels=x, hoverinfo='all', textinfo='label+percent+value',
                                           textfont_size=15, textfont_color='white', textposition='inside', showlegend=False, hole=.4)])
            fig04.update_layout(title='Proportions of Trade(Recovered)', annotations=[dict(text='Recovered', x=0.5, y=0.5, font_color='white', font_size=15, showarrow=False)])
            fig04.update_traces(marker=dict(colors=colorpierecoveredtier1))
            st.plotly_chart(fig04, use_container_width=True)

        with fig05, _lock:
            fig05 = go.Figure(data=[go.Bar(x=x, y=y5, orientation='v', text=y5, textfont = dict(family='sana serif', size=14, color='#c4fff7'),
                                    textposition='auto', textangle = -45, texttemplate = '%{text:.2f}')])
            fig05.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolor, showgrid=False,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig05.update_yaxes(title_text='Mean Time Spent', title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig05.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity02)
            fig05.update_layout(title='Mean Time Spent to Recovered(hrs)', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig05, use_container_width=True)

        with fig06, _lock:
            fig06 = go.Figure(data=[go.Bar(x=x, y=y6, orientation='v', text=y6,
                                    textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                    textposition='auto', textangle = -45, texttemplate = '%{text:.2f}')])
            fig06.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig06.update_yaxes(title_text='Total Time Spent', title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig06.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig06.update_layout(title='Total Time Spent to Recovered(hrs)', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig06, use_container_width=True)

        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_Tier2, unsafe_allow_html=True)
        st.markdown('##')

        groupcategory_usecols = ['Trade_Category', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']

        df7 = df4[groupcategory_usecols].groupby(by=['Trade_Category']).agg(['count', 'max', 'min', 'mean', 'sum']).sort_values((     'Time_Acknowledged_hrs', 'count'), ascending=False)
        cols_name01 = ['Fault_Acknowledged_count', 'Fault_Acknowledged_max(hrs)', 'Fault_Acknowledged_min(hrs)', 'Fault_Acknowledged_mean(hrs)',
                       'Fault_Acknowledged_sum(hrs)', 'Fault_Site_Reached_count', 'Fault_Site_Reached_max(hrs)', 'Fault_Site_Reached_min(hrs)',
                       'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)', 'Fault_Work_Started_count', 'Fault_Work_Started_max(hrs)',
                       'Fault_Work_Started_min(hrs)', 'Fault_Work_Started_mean(hrs)', 'Fault_Work_Started_sum(hrs)', 'Fault_Recovered_count',
                       'Fault_Recovered_max(hrs)', 'Fault_Recovered_min(hrs)', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']
        df7.columns = cols_name01
        df8 = df7.loc[:, ['Fault_Site_Reached_count', 'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)',
                     'Fault_Recovered_count', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']].copy()
        df8.reset_index(inplace=True)

        df_fig10 = df8.loc[:, ['Trade_Category', 'Fault_Recovered_count']].sort_values('Fault_Recovered_count', ascending=False).head(10)
        df_fig11 = df8.loc[:, ['Trade_Category', 'Fault_Recovered_mean(hrs)']].sort_values('Fault_Recovered_mean(hrs)', ascending=False).head(10)
        df_fig12 = df8.loc[:, ['Trade_Category', 'Fault_Recovered_sum(hrs)']].sort_values('Fault_Recovered_sum(hrs)', ascending=False).head(10)

        x_fig10 = df_fig10.Trade_Category
        y_fig10 = df_fig10['Fault_Recovered_count']
        x_fig11 = df_fig11.Trade_Category
        y_fig11 = df_fig11['Fault_Recovered_mean(hrs)']
        x_fig12 = df_fig12.Trade_Category
        y_fig12 = df_fig12['Fault_Recovered_sum(hrs)']

        fig10, fig11, fig12 = st.columns(3)
        with fig10, _lock:
            fig10 = go.Figure(data=[go.Bar(x=x_fig10, y=y_fig10, orientation='v', text=y_fig10,
                                   textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                   textposition='auto', textangle=-45)])
            fig10.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig10.update_yaxes(title_text='Count(Recovered)', title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig10.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity01)
            fig10.update_layout(title='Count(Recovered)-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig10, use_container_width=True)

        with fig11, _lock:
            fig11 = go.Figure(data=[go.Bar(x=x_fig11, y=y_fig11, orientation='v', text=y_fig11,
                                    textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                    textposition='auto', textangle=-45, texttemplate='%{text:.2f}')])
            fig11.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig11.update_yaxes(title_text='Mean Time Spent', title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig11.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity02)
            fig11.update_layout(title='Mean Time Spent to Recovered(hrs)-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig11, use_container_width=True)

        with fig12, _lock:
            fig12 = go.Figure(data=[go.Bar(x=x_fig12, y=y_fig12, orientation='v', text=y_fig12,
                                   textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                   textposition='auto', textangle=-45, texttemplate='%{text:.2f}')])
            fig12.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig12.update_yaxes(title_text='Total Time Spent', title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig12.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig12.update_layout(title='Total Time Spent to Recovered(hrs)-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig12, use_container_width=True)

        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_Tier3, unsafe_allow_html=True)
        st.markdown('##')

        grouptypeoffault_usecols = ['Type_of_Fault', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']

        df9 = df4[grouptypeoffault_usecols].groupby(by=['Type_of_Fault']).agg(['count', 'max', 'min', 'mean', 'sum']).sort_values((     'Time_Acknowledged_hrs', 'count'), ascending=False)
        cols_name02 = ['Fault_Acknowledged_count', 'Fault_Acknowledged_max(hrs)', 'Fault_Acknowledged_min(hrs)', 'Fault_Acknowledged_mean(hrs)',
                       'Fault_Acknowledged_sum(hrs)', 'Fault_Site_Reached_count', 'Fault_Site_Reached_max(hrs)', 'Fault_Site_Reached_min(hrs)',
                       'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)', 'Fault_Work_Started_count', 'Fault_Work_Started_max(hrs)',
                       'Fault_Work_Started_min(hrs)', 'Fault_Work_Started_mean(hrs)', 'Fault_Work_Started_sum(hrs)', 'Fault_Recovered_count',
                       'Fault_Recovered_max(hrs)', 'Fault_Recovered_min(hrs)', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']
        df9.columns = cols_name02
        df10 = df9.loc[:, ['Fault_Site_Reached_count', 'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)',
                     'Fault_Recovered_count', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']]
        df10.reset_index(inplace=True)

        df_fig16 = df10.loc[:, ['Type_of_Fault', 'Fault_Recovered_count']].sort_values('Fault_Recovered_count', ascending=False).head(10)
        df_fig17 = df10.loc[:, ['Type_of_Fault', 'Fault_Recovered_mean(hrs)']].sort_values('Fault_Recovered_mean(hrs)', ascending=False).head(10)
        df_fig18 = df10.loc[:, ['Type_of_Fault', 'Fault_Recovered_sum(hrs)']].sort_values('Fault_Recovered_sum(hrs)', ascending=False).head(10)


        x_fig16 = df_fig16.Type_of_Fault
        y_fig16 = df_fig16['Fault_Recovered_count']
        x_fig17 = df_fig17.Type_of_Fault
        y_fig17 = df_fig17['Fault_Recovered_mean(hrs)']
        x_fig18 = df_fig18.Type_of_Fault
        y_fig18 = df_fig18['Fault_Recovered_sum(hrs)']

        fig16, fig17, fig18 = st.columns(3)
        with fig16, _lock:
            fig16 = go.Figure(data=[go.Bar(x=x_fig16, y=y_fig16, orientation='v', text=y_fig16,
                                 textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                 textposition='auto', textangle=-45)])
            fig16.update_xaxes(title_text="Type of Fault", tickangle=-45, title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig16.update_yaxes(title_text='Count(Recovered)', title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig16.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity01)
            fig16.update_layout(title='Count(Recovered)-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig16, use_container_width=True)

        with fig17, _lock:
            fig17 = go.Figure(data=[go.Bar(x=x_fig17, y=y_fig17, orientation='v', text=y_fig17,
                                 textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                 textposition='auto', textangle=-45, texttemplate='%{text:.2f}')])
            fig17.update_xaxes(title_text="Type of Fault", tickangle=-45, title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig17.update_yaxes(title_text='Mean Time Spent', title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig17.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity02)
            fig17.update_layout(title='Mean Time Spent to Recovered(hrs)-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig17, use_container_width=True)

        with fig18, _lock:
            fig18 = go.Figure(data=[go.Bar(x=x_fig18, y=y_fig18, orientation='v', text=y_fig18,
                                 textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                 textposition='auto', textangle=-45, texttemplate='%{text:.2f}')])
            fig18.update_xaxes(title_text="Type of Fault", tickangle=-45, title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig18.update_yaxes(title_text='Total Time Spent', title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig18.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig18.update_layout(title='Total Time Spent to Recovered(hrs)-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig18, use_container_width=True)


    #-------------------------------------------Fault vs Location-----------------------------------------------
        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_location, unsafe_allow_html=True)
        st.markdown('##')

        ## groupby building
        groupbuilding_usecols = ['Building', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']

        df11 = df4[groupbuilding_usecols].groupby(by=['Building']).agg(['count', 'max', 'min', 'mean', 'sum'])
        cols_name_building = ['Fault_Acknowledged_count', 'Fault_Acknowledged_max(hrs)', 'Fault_Acknowledged_min(hrs)', 'Fault_Acknowledged_mean(hrs)',
                       'Fault_Acknowledged_sum(hrs)', 'Fault_Site_Reached_count', 'Fault_Site_Reached_max(hrs)', 'Fault_Site_Reached_min(hrs)',
                       'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)', 'Fault_Work_Started_count', 'Fault_Work_Started_max(hrs)',
                       'Fault_Work_Started_min(hrs)', 'Fault_Work_Started_mean(hrs)', 'Fault_Work_Started_sum(hrs)', 'Fault_Recovered_count',
                       'Fault_Recovered_max(hrs)', 'Fault_Recovered_min(hrs)', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']
        df11.columns = cols_name_building
        df12 = df11.loc[:, ['Fault_Recovered_count', 'Fault_Recovered_sum(hrs)']]

        x_fig19 = df12['Fault_Recovered_count'].sort_values().index
        y_fig19 = df12['Fault_Recovered_count'].sort_values().values

        x_fig20 = df12['Fault_Recovered_sum(hrs)'].sort_values().index
        y_fig20 = df12['Fault_Recovered_sum(hrs)'].sort_values().values


        fig19, fig20 = st.columns(2)
        with fig19, _lock:
            fig19 = go.Figure(data=[go.Bar(x=y_fig19, y=x_fig19, orientation='h', text=y_fig19,
                                 textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                 textposition='auto', textangle=0)])
            fig19.update_xaxes(title_text="Number of Fault", title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig19.update_yaxes(title_text='Building', title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickmode='linear')
            fig19.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity02)
            fig19.update_layout(title='Number of Fault vs Building', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig19, use_container_width=True)

        with fig20, _lock:
            fig20 = go.Figure(data=[go.Bar(x=y_fig20, y=x_fig20, orientation='h', text=y_fig20,
                                   textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                   textposition='auto', textangle=0, texttemplate='%{text:.2f}')])
            fig20.update_xaxes(title_text="Total Time Spent", title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig20.update_yaxes(title_text='Building', title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickmode='linear')
            fig20.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig20.update_layout(title='Total Time Spent(hrs) vs Building', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig20, use_container_width=True)

    ## groupby building floor

        df4['buildingfloor'] = df4.Building + '-' + df4.Floor

        groupbuildingfloor_usecols = ['buildingfloor', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']
        
        df13 = df4[groupbuildingfloor_usecols].groupby(by=['buildingfloor']).agg(['count', 'max', 'min', 'mean', 'sum'])
        cols_name_buildingfloor = ['Fault_Acknowledged_count', 'Fault_Acknowledged_max(hrs)', 'Fault_Acknowledged_min(hrs)', 'Fault_Acknowledged_mean(hrs)',
                       'Fault_Acknowledged_sum(hrs)', 'Fault_Site_Reached_count', 'Fault_Site_Reached_max(hrs)', 'Fault_Site_Reached_min(hrs)',
                       'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)', 'Fault_Work_Started_count', 'Fault_Work_Started_max(hrs)',
                       'Fault_Work_Started_min(hrs)', 'Fault_Work_Started_mean(hrs)', 'Fault_Work_Started_sum(hrs)', 'Fault_Recovered_count',
                       'Fault_Recovered_max(hrs)', 'Fault_Recovered_min(hrs)', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']
        df13.columns = cols_name_buildingfloor
        df14 = df13.loc[:, ['Fault_Recovered_count', 'Fault_Recovered_sum(hrs)']].sort_values(by=['Fault_Recovered_count'], ascending=False).head(10)
        df14_sum = df13.loc[:, ['Fault_Recovered_count','Fault_Recovered_sum(hrs)']].sort_values(by=['Fault_Recovered_sum(hrs)'], ascending=False).head(10)

        x_fig21 = df14['Fault_Recovered_count'].sort_values(ascending=True).index
        y_fig21 = df14['Fault_Recovered_count'].sort_values(ascending=True).values

        x_fig22 = df14_sum['Fault_Recovered_sum(hrs)'].sort_values(ascending=True).index
        y_fig22 = df14_sum['Fault_Recovered_sum(hrs)'].sort_values(ascending=True).values


        fig21, fig22 = st.columns(2)
        with fig21, _lock:
            fig21 = go.Figure(data=[go.Bar(x=y_fig21, y=x_fig21, orientation='h', text=y_fig21,
                                 textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                 textposition='auto', textangle=0)])
            fig21.update_xaxes(title_text="Number of Fault", title_font_color=titlefontcolor, showgrid=True,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig21.update_yaxes(title_text='Floor', title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickmode='linear')
            fig21.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity02)
            fig21.update_layout(title='Number of Fault vs Building& Floor-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig21, use_container_width=True)

        with fig22, _lock:
            fig22 = go.Figure(data=[go.Bar(x=y_fig22, y=x_fig22, orientation='h', text=y_fig22,
                                   textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                   textposition='auto', textangle=0, texttemplate='%{text:.2f}')])
            fig22.update_xaxes(title_text="Total Time Spent", title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig22.update_yaxes(title_text='Floor', title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickmode='linear')
            fig22.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig22.update_layout(title='Total Time Spent(hrs) vs Building& Floor-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig22, use_container_width=True)


    ## groupby building floor room
        df4['buildingfloorroom'] = df4.Building + '-' + df4.Floor + '-' + df4.Room

        groupbuildingfloorroom_usecols = ['buildingfloorroom', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']

        df15 = df4[groupbuildingfloorroom_usecols].groupby(by=['buildingfloorroom']).agg(['count', 'max', 'min', 'mean', 'sum'])
        cols_name_buildingfloorroom = ['Fault_Acknowledged_count', 'Fault_Acknowledged_max(hrs)', 'Fault_Acknowledged_min(hrs)', 'Fault_Acknowledged_mean(hrs)',
                       'Fault_Acknowledged_sum(hrs)', 'Fault_Site_Reached_count', 'Fault_Site_Reached_max(hrs)', 'Fault_Site_Reached_min(hrs)',
                       'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)', 'Fault_Work_Started_count', 'Fault_Work_Started_max(hrs)',
                       'Fault_Work_Started_min(hrs)', 'Fault_Work_Started_mean(hrs)', 'Fault_Work_Started_sum(hrs)', 'Fault_Recovered_count',
                       'Fault_Recovered_max(hrs)', 'Fault_Recovered_min(hrs)', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']
        df15.columns = cols_name_buildingfloorroom

        df16 = df15.loc[:, ['Fault_Recovered_count', 'Fault_Recovered_sum(hrs)']].sort_values('Fault_Recovered_count', ascending=False).head(10)
        df17 = df15.loc[:, ['Fault_Recovered_count', 'Fault_Recovered_sum(hrs)']].sort_values('Fault_Recovered_sum(hrs)',ascending=False).head(10)

        x_fig23 = df16['Fault_Recovered_count'].sort_values(ascending=True).index
        y_fig23 = df16['Fault_Recovered_count'].sort_values(ascending=True).values

        x_fig24 = df17['Fault_Recovered_sum(hrs)'].sort_values(ascending=True).index
        y_fig24 = df17['Fault_Recovered_sum(hrs)'].sort_values(ascending=True).values


        fig23, fig24 = st.columns(2)
        with fig23, _lock:
            fig23 = go.Figure(data=[go.Bar(x=y_fig23, y=x_fig23, orientation='h', text=y_fig23,
                                 textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                 textposition='auto', textangle=0)])
            fig23.update_xaxes(title_text="Number of Fault", title_font_color=titlefontcolor, showgrid=True,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig23.update_yaxes(title_text='Room', title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickmode='linear')
            fig23.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity02)
            fig23.update_layout(title='Number of Fault vs Building Floor& Room-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig23, use_container_width=True)

        with fig24, _lock:
            fig24 = go.Figure(data=[go.Bar(x=y_fig24, y=x_fig24, orientation='h', text=y_fig24,
                                   textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                   textposition='auto', textangle=0, texttemplate='%{text:.1f}')])
            fig24.update_xaxes(title_text="Total Time Spent", title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig24.update_yaxes(title_text='Room', title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickmode='linear')
            fig24.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig24.update_layout(title='Total Time Spent(hrs) vs Building Floor& Room-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig24, use_container_width=True)




#------------------------------------Number of fault vs people & wordcloud--------------------------------------
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
        st.markdown(html_card_subheader_fault_Technician, unsafe_allow_html=True)
        st.markdown('##')

        Abala = df3[df3.Remarks.str.contains('abala|Abala|A.bala|a.bala|A.Bala')].shape[0]
        Allan = df3[df3.Remarks.str.contains('Allan|allan|allen|Allen|alan|alen')].shape[0]
        Aru = df3[df3.Remarks.str.contains('Aru|aru')].shape[0]
        Hossain = df3[df3.Remarks.str.contains('Hossain|hossain')].shape[0]
        Ilayaraja = df3[df3.Remarks.str.contains('Ilayaraja|ilayaraja')].shape[0]
        Isyamudin = df3[df3.Remarks.str.contains('Isyamudin|isyamudin|lsyamudin|Lsyamudin')].shape[0]
        Lifei = df3[df3.Remarks.str.contains('Lifei|lifei|Li Fei|Li fei|li fei')].shape[0]
        Mani = df3[df3.Remarks.str.contains('Mani|mani')].shape[0]
        Mingcai = df3[df3.Remarks.str.contains('Mingcai|mingcai|Ming Cai|Ming cai|ming cai')].shape[0]
        Nazri = df3[df3.Remarks.str.contains('Nazri|nazri')].shape[0]
        Satha = df3[df3.Remarks.str.contains('Satha|satha')].shape[0]
        Senthil = df3[df3.Remarks.str.contains('Senthil|senthil')].shape[0]
        Shanmu = df3[df3.Remarks.str.contains('Shanmu|shanmu')].shape[0]
        Su = df3[df3.Remarks.str.contains('-Su|-su|- Su|- su')].shape[0]
        Vbala = df3[df3.Remarks.str.contains('Vbala|vbala|V.bala|v.bala|V.Bala')].shape[0]
        Jailani = df3[df3.Remarks.str.contains('Jailani|jailani|Jailan|jailan|Jailan|jailan')].shape[0]
        Packiyaraj = df3[df3.Remarks.str.contains('Packiyaraj|packiyaraj')].shape[0]
        Ela = df3[df3.Remarks.str.contains('Ela|ela')].shape[0]
        FRC = df3[df3.Remarks.str.contains('FRC|frc')].shape[0]
        Thandapani = df3[df3.Remarks.str.contains('Thandapani|thandapani')].shape[0]
        Gary = df3[df3.Remarks.str.contains('Gary|gary')].shape[0]
        Murugan = df3[df3.Remarks.str.contains('Murugan|murugan')].shape[0]
        Rabart = df3[df3.Remarks.str.contains('Rabart|rabart')].shape[0]
        Dutytech = df3[df3.Remarks.str.contains('Dutytech|dutytech')].shape[0]
     

        x_people = ['Abala', 'Allan', 'Aru', 'Hossain', 'Ilayaraja', 'Isyamudin', 'LiFei', 'Mani', 'Mingcai', 'Nazri', 'Satha', 'Senthil', 'Shanmu', 'Su', 'Vbala', 'Jailani', 'Packiyaraj', 'Ela', 'FRC', 'Thandapani', 'Gary', 'Murugan', 'Rabart', 'Dutytech']
        y_people = [Abala, Allan, Aru, Hossain, Ilayaraja, Isyamudin, Lifei, Mani, Mingcai, Nazri, Satha, Senthil, Shanmu, Su, Vbala, Jailani, Packiyaraj, Ela, FRC, Thandapani, Gary, Murugan, Rabart, Dutytech]
        y_people_sum = sum(y_people)

        st.markdown(f"Total Fault = {y_people_sum}")

        # column01_people, column02_people, column03_people, column04_people, column05_people, column06_people, column07_people, \
        # column08_people, column09_people, column10_people, column11_people, column12_people, column13_people,column14_people, column15_people = st.columns(15)
        # with column01_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Abala</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Abala}</h2>", unsafe_allow_html=True)

        # with column02_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Allan</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Allan}</h2>", unsafe_allow_html=True)

        # with column03_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Aru</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Aru}</h2>", unsafe_allow_html=True)

        # with column04_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Hossain</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Hossain}</h2>", unsafe_allow_html=True)

        # with column05_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Ilayaraja</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Ilayaraja}</h2>", unsafe_allow_html=True)

        # with column06_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Isyamudin</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Isyamudin}</h2>", unsafe_allow_html=True)

        # with column07_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Lifei</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Lifei}</h2>", unsafe_allow_html=True)

        # with column08_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Mani</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Mani}</h2>", unsafe_allow_html=True)

        # with column09_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Mingcai</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Mingcai}</h2>", unsafe_allow_html=True)

        # with column10_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Nazri</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Nazri}</h2>", unsafe_allow_html=True)

        # with column11_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Satha</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Satha}</h2>", unsafe_allow_html=True)

        # with column12_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Senthil</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Senthil}</h2>", unsafe_allow_html=True)

        # with column13_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Shanmu</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Shanmu}</h2>", unsafe_allow_html=True)

        # with column14_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Su</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Su}</h2>", unsafe_allow_html=True)

        # with column15_people, _lock:
        #     st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Vbala</h6>", unsafe_allow_html=True)
        #     st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{Vbala}</h2>", unsafe_allow_html=True)

        st.markdown('##')
        st.markdown('##')
        fig25, wc = st.columns(2)
        with fig25, _lock:
            fig25 = go.Figure(data=[go.Bar(x=x_people, y=y_people, orientation='v', text=y_people,
                                           textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                           textposition='auto', textangle=-45)])
            fig25.update_xaxes(title_text="Name", title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis,
                               linecolor=linecolor_xy_axis, tickangle=-45)
            fig25.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=False,
                               gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis,
                               linecolor=linecolor_xy_axis)
            fig25.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor,
                                marker_line_width=markerlinewidth, opacity=opacity03)
            fig25.update_layout(title='Number of Fault vs Name', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig25, use_container_width=True)

        with wc, _lock:
            st.markdown('**Actions Taken**')
            stopwords = ['done', 'Done', 'check', 'Found', 'found', 'from', 'have',
                         'in', 'on', 'at', 'make', 'it', 'the', 'and', 'to', 'for', 'need']
            wc = WordCloud(background_color='#0e1117', stopwords= stopwords, colormap='Set2', width = 1920, height = 1200).generate(str(df2['Action(s)_Taken'].values))
            st.image(wc.to_array(), width=650)




        # st.markdown('##')
        # st.markdown('##')
        # x_technician = df.Attended_By.value_counts().index
        # y_technician = df.Attended_By.value_counts().values
        # fig26 = go.Figure(data=[go.Bar(x=x_technician, y=y_technicain, orientation='v', text=y_technicain,
        #                                 textfont=dict(family='sana serif', size=14, color='#c4fff7'),
        #                                 textposition='auto', textangle=-45)])
        # fig26.update_xaxes(title_text="Name", title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
        #                     gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis,
        #                     linecolor=linecolor_xy_axis, tickangle=-45)
        # fig26.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=False,
        #                     gridwidth=gridwidth,
        #                     gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis,
        #                     linecolor=linecolor_xy_axis)
        # fig26.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor,
        #                     marker_line_width=markerlinewidth, opacity=opacity03)
        # fig26.update_layout(title='Number of Fault vs Name', plot_bgcolor=plot_bgcolor)
        # st.plotly_chart(fig26, use_container_width=True)


# =======================================Schedule===================================================================
    if page =='Schedules':
        def fetch_file_schedules(filename):
            cols = ['Schedule ID', 'Trade', 'Trade Category', 'Strategic Partner',
               'Frequency', 'Description', 'Type', 'Scope', 'Site', 'Building',
               'Floor', 'Room', 'Start Date',
               'End Date', 'Work Started Date', 'Work Completed Date',
               'Attended By', 'Portal ID', 'Service Report Completed Date',
               'Total Number of Service Reports',
               'Total Number of Quantity in Service Reports', 'Asset Tag Number',
               'Alert Case']
            parse_dates = ['Start Date', 'End Date', 'Work Started Date', 'Work Completed Date',
                           'Service Report Completed Date']
            dtype_cols = {'Site': 'str', 'Building': 'str', 'Floor': 'str', 'Room': 'str'}
            return pd.read_excel(filename, header=0, index_col='Schedule ID', usecols=cols, parse_dates=parse_dates, dtype=dtype_cols)

        dfs = fetch_file_schedules('schedules_RMG.xlsx')
        dfs.columns = dfs.columns.str.replace(' ', '_')
        dfs['Time_Work_Completed_hrs'] = (dfs.Work_Completed_Date - dfs.Work_Started_Date) / pd.Timedelta(hours=1)

    # ----------------------------------------Sidebar---------------------------------------------------------------------
        st.sidebar.header('Please Filter Here:')

        Trade = st.sidebar.multiselect(
            'Select the Trade:',
            options=dfs['Trade'].unique(),
            default=dfs['Trade'].unique()
        )

        Trade_Category = st.sidebar.multiselect(
            'Select the Trade Category:',
            options=dfs['Trade_Category'].unique(),
            default=dfs['Trade_Category'].unique()
        )

        dfs = dfs.query(
            'Trade ==@Trade & Trade_Category==@Trade_Category'
        )
     # ----------------------------------------Main page-----------------------------------------------------------
        html_card_title_schedules="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; padding-top: 5px; width: 800px;
           height: 50px;">
            <h1 class="card-title" style=color:#4c9085; font-family:Georgia; text-align: left; padding: 0px 0;">SCHEDULES DASHBOARD</h1>
          </div>
        </div>
        """
        st.markdown(html_card_title_schedules, unsafe_allow_html=True)
        st.markdown('##')
        st.markdown('##')

        total_schedule = dfs.shape[0]
        schedule_outstanding = dfs[dfs['Work_Completed_Date'].isna()].shape[0]
        schedule_completed = dfs[dfs['Work_Completed_Date'].notna()].shape[0]
        total_SR = dfs.Total_Number_of_Service_Reports.sum()
        # total_asset =
        alert_case = int(dfs['Alert_Case'].sum())

        column01_schedule, column02_schedule, column03_schedule, column04_schedule, column05_schedule = st.columns(5)
        with column01_schedule, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #4c9085;'>Total</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #4c9085;'>{total_schedule}</h2>", unsafe_allow_html=True)

        with column02_schedule, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #4c9085;'>Outstanding</h6>",unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #4c9085;'>{schedule_outstanding}</h2>", unsafe_allow_html=True)

        with column03_schedule, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #4c9085;'>Completed</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #4c9085;'>{schedule_completed}</h2>", unsafe_allow_html=True)

        with column04_schedule, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #4c9085;'>Alert</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: red;'>{alert_case}</h2>", unsafe_allow_html=True)

        with column05_schedule, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #4c9085;'>No.of SR</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #4c9085;'>{total_SR}</h2>", unsafe_allow_html=True)

        html_card_subheader_outstanding_schedules="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #4c9085; padding-top: 5px; width: 350px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#4c9085; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Outstanding Schedules</h3>
          </div>
        </div>
        """
        html_card_subheader_daily_schedules="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #4c9085; padding-top: 5px; width: 350px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#4c9085; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Daily Schedule Cases</h3>
          </div>
        </div>
        """
        html_card_subheader_schedules_Tier1="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #4c9085; padding-top: 5px; width: 500px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#4c9085; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Completed Schedules vs Trade</h3>
          </div>
        </div>
        """
        html_card_subheader_schedules_Tier2="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #4c9085; padding-top: 5px; width: 600px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#4c9085; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Completed Schedules vs Trade Category</h3>
          </div>
        </div>
        """
        html_card_subheader_schedules_Technician="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #4c9085; padding-top: 5px; width: 650px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#4c9085; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">No.of Completed Schedules vs Technician</h3>
          </div>
        </div>
        """
#--------------------------------------- color & width & opacity----------------------------------------------
        # Pie chart
        colorpieoutstandings = ['#4c9085', '#1dacd6', '#50a747', '#59656d', '#06c2ac', '#137e6d', '#929906', '#ff9408']
        colorpierecoveredstier1 = ['#4c9085', '#1dacd6', '#50a747', '#59656d', '#06c2ac', '#137e6d', '#929906', '#ff9408']

        # all barchart and linechart
        titlefontcolors = '#4c9085'
        gridwidths = 0.1
        gridcolors = '#1f3b4d'
        plot_bgcolors = 'rgba(0,0,0,0)'

        # x&y axis width and color
        linewidths_xy_axis = 1
        linecolors_xy_axis = '#59656d'

        # all barchart
        markercolors = '#4c9085'
        markerlinecolors = '#4c9085'
        markerlinewidths = 1

        #linechart
        linecolors = '#4c9085'
        linewidths = 2
#------------------------------------------ Outstanding Schedules-------------------------------------------------

        st.markdown('##')
        st.markdown('##')
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """,
                    unsafe_allow_html=True)
        st.markdown(html_card_subheader_outstanding_schedules, unsafe_allow_html=True)
        st.markdown('##')

        dfs_outstanding = dfs[dfs['Work_Completed_Date'].isna()]

        props = 'font-style: italic; color: #ffffff; font-size:0.8em; font-weight:normal;'  #border: 0.0001px solid #116a8c; background: #116a8c'
        dfs_outstandingdataframe = dfs_outstanding.style.applymap(lambda x: props)
        st.dataframe(dfs_outstandingdataframe, 2000, 200)

        # sers_outstanding_building = dfs_outstanding.groupby(['Trade'])['Trade_Category'].count().sort_values(ascending=False)
        # sers_outstanding_category = dfs_outstanding.groupby(['Trade_Category'])['Trade'].count().sort_values(ascending=False)

        # xs_outstanding_building = sers_outstanding_building.index
        # ys_outstanding_building = sers_outstanding_building.values
        # xs_outstanding_category = sers_outstanding_category.index
        # ys_outstanding_category = sers_outstanding_category.values

        # figs_outstanding_building, figs_outstanding_category = st.columns([1, 2])

        # with figs_outstanding_building, _lock:
        #     figs_outstanding_building = go.Figure(data=[go.Pie(labels=xs_outstanding_building, values=ys_outstanding_building, hoverinfo='all', textinfo='label+percent+value',
        #                                                        textfont_size=15, textfont_color='white', textposition='inside', showlegend=False, hole=.4)])
        #     figs_outstanding_building.update_layout(title='Number of Schedule vs Trade', annotations=[dict(text='Outstanding', x=0.5, y=0.5, font_size=15, font_color='white', showarrow=False)])
        #     figs_outstanding_building.update_traces(marker=dict(colors=colorpieoutstandings))
        #     st.plotly_chart(figs_outstanding_building, use_container_width=True)

        # with figs_outstanding_category, _lock:
        #     figs_outstanding_category = go.Figure(data=[go.Bar(x=xs_outstanding_category, y=ys_outstanding_category, orientation='v',
        #                                                        text=ys_outstanding_category,textfont=dict(family='sana serif', size=14, color='#c4fff7'),
        #                                                        textposition='auto', textangle=-45)
        #                                                 ])
        #     figs_outstanding_category.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolors, showgrid=False, gridwidth=gridwidths,
        #                        gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
        #     figs_outstanding_category.update_yaxes(title_text='Number of Schedule', title_font_color=titlefontcolors, showgrid=True, gridwidth=gridwidths,
        #                        gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
        #     figs_outstanding_category.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
        #     figs_outstanding_category.update_layout(title='Number of Schedule vs Trade Category', plot_bgcolor=plot_bgcolors)
        #     st.plotly_chart(figs_outstanding_category, use_container_width=True)

# ------------------------------------------ Daily Schedules-------------------------------------------------
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
        st.markdown(html_card_subheader_daily_schedules, unsafe_allow_html=True)
        st.markdown('##')

        dfs_completed = dfs[dfs['Work_Completed_Date'].notna()].loc[:, ['Trade', 'Trade_Category', 'Work_Started_Date', 'Time_Work_Completed_hrs', 'Attended_By']]


        xs_daily = dfs_completed['Work_Started_Date'].dt.day.value_counts().sort_index().index
        ys_daily = dfs_completed['Work_Started_Date'].dt.day.value_counts().sort_index().values
        ys_mean = dfs_completed['Work_Started_Date'].dt.day.value_counts().sort_index().mean()

        day_max_s = dfs_completed.Work_Started_Date.dt.day.max()

        figs_daily = go.Figure(data=go.Scatter(x=xs_daily, y=ys_daily, mode='lines+markers+text', line=dict(color=linecolors, width=linewidths),
                                text=ys_daily, textfont=dict(family='sana serif', size=14, color='#c4fff7'), textposition='top center'))
        figs_daily.add_hline(y=ys_mean, line_dash='dot', line_color='#96ae8d', line_width=2, annotation_text='Average Line',
                                annotation_position='bottom right', annotation_font_size=18, annotation_font_color='green')
        figs_daily.update_xaxes(title_text='Date', tickangle=-45, title_font_color=titlefontcolors, tickmode='linear',
                                   range=[1, day_max_s], showgrid=False, gridwidth=gridwidths, gridcolor=gridcolors,
                                showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
        figs_daily.update_yaxes(title_text='Number of Schedule', title_font_color=titlefontcolors, tickmode='linear', showgrid=False,
                                gridwidth=gridwidths, gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
        figs_daily.update_layout(title='Number of Schedule vs Date', plot_bgcolor=plot_bgcolors,
                                 # xaxis=dict(showticklabels=True, ticks='outside', tickfont=dict(family='Arial', size=12, color='rgb(82, 82, 82)')),
                                 # yaxis=dict(showticklabels=True, ticks='outside', tickfont=dict(family='Arial', size=12, color='rgb(82, 82, 82)'))
                                 )
        st.plotly_chart(figs_daily, use_container_width=True)

# ------------------------------------------ Schedules Tier1 & Tier2-------------------------------------------------
        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_schedules_Tier1, unsafe_allow_html=True)
        st.markdown('##')

        groupscheduletrade_usecols = ['Trade', 'Time_Work_Completed_hrs']

        dfs1 = dfs_completed[groupscheduletrade_usecols].groupby(by=['Trade']).agg(['count', 'max', 'min', 'mean', 'sum']).sort_values(('Time_Work_Completed_hrs', 'count'), ascending=False)
        col_name_s1 = ['Schedule_Completed_count', 'Time_Schedule_Completed_max(hrs)', 'Time_Schedule_Completed_min(hrs)',
                       'Time_Schedule_Completed_mean(hrs)', 'Time_Schedule_Completed_sum(hrs)']
        dfs1.columns = col_name_s1

        dfs1.reset_index(inplace=True)

        xs1 = dfs1['Trade']
        ys1 = dfs1['Schedule_Completed_count']
        ys2 = dfs1['Time_Schedule_Completed_mean(hrs)']
        ys3 = dfs1['Time_Schedule_Completed_sum(hrs)']

        figs01, figs02, figs03 = st.columns(3)
        with figs01, _lock:
            figs01 = go.Figure(data=[go.Pie(values=ys1, labels=xs1, hoverinfo='all', textinfo='label+percent+value', textfont_size=15, textfont_color='white', textposition='inside', showlegend=False, hole=.4)])
            figs01.update_layout(title='Proportions of Trade', annotations=[dict(text='Completed', x=0.5, y=0.5, font_size=15, font_color='white', showarrow=False)])
            figs01.update_traces(marker=dict(colors=colorpierecoveredstier1))
            st.plotly_chart(figs01, use_container_width=True)

        with figs02, _lock:
            figs02 = go.Figure(data=[go.Bar(x=xs1, y=ys2, orientation='v', text=ys2,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45, texttemplate='%{text:.2f}')
                                     ])
            figs02.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolors, showgrid=False, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs02.update_yaxes(title_text='Mean Time Spent(hrs)', title_font_color=titlefontcolors, showgrid=True, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs02.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
            figs02.update_layout(title='Mean Time Spent to Complete(hrs)', plot_bgcolor=plot_bgcolors)
            st.plotly_chart(figs02, use_container_width=True)

        with figs03, _lock:
            figs03 = go.Figure(data=[go.Bar(x=xs1, y=ys3, orientation='v', text=ys3,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45, texttemplate='%{text:.2f}')
                                     ])
            figs03.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolors, showgrid=False, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs03.update_yaxes(title_text='Total Time Spent(hrs)', title_font_color=titlefontcolors, showgrid=True, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs03.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
            figs03.update_layout(title='Total Time Spent to Complete(hrs)', plot_bgcolor=plot_bgcolors)
            st.plotly_chart(figs03, use_container_width=True)

        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_schedules_Tier2, unsafe_allow_html=True)
        st.markdown('##')
        
        groupschedulecategory_usecols = ['Trade_Category', 'Time_Work_Completed_hrs']
        dfs2 = dfs_completed[groupschedulecategory_usecols].groupby(by=['Trade_Category']).agg(['count', 'max', 'min', 'mean', 'sum'])
        col_name_s2 = ['Schedule_Completed_count', 'Time_Schedule_Completed_max(hrs)', 'Time_Schedule_Completed_min(hrs)', 'Time_Schedule_Completed_mean(hrs)', 'Time_Schedule_Completed_sum(hrs)']
        dfs2.columns = col_name_s2
        dfs2.reset_index(inplace=True)

        dfs_fig04 = dfs2.loc[:, ['Trade_Category', 'Schedule_Completed_count']].sort_values('Schedule_Completed_count', ascending=False).head(10)
        dfs_fig05 = dfs2.loc[:, ['Trade_Category', 'Time_Schedule_Completed_mean(hrs)']].sort_values('Time_Schedule_Completed_mean(hrs)', ascending=False).head(10)
        dfs_fig06 = dfs2.loc[:, ['Trade_Category', 'Time_Schedule_Completed_sum(hrs)']].sort_values('Time_Schedule_Completed_sum(hrs)', ascending=False).head(10)

        xs_fig04 = dfs_fig04['Trade_Category']
        ys_fig04 = dfs_fig04['Schedule_Completed_count']

        xs_fig05 = dfs_fig05['Trade_Category']
        ys_fig05 = dfs_fig05['Time_Schedule_Completed_mean(hrs)']

        xs_fig06 = dfs_fig06['Trade_Category']
        ys_fig06 = dfs_fig06['Time_Schedule_Completed_sum(hrs)']

        figs04, figs05, figs06 = st.columns(3)
        with figs04, _lock:
            figs04 = go.Figure(data=[go.Bar(x=xs_fig04, y=ys_fig04, orientation='v', text=ys_fig04,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45)
                                     ])
            figs04.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolors, showgrid=False,
                                gridwidth=gridwidths, gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs04.update_yaxes(title_text='Count', title_font_color=titlefontcolors, showgrid=True, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs04.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
            figs04.update_layout(title='Count-Top 10', plot_bgcolor=plot_bgcolors)
            st.plotly_chart(figs04, use_container_width=True)

        with figs05, _lock:
            figs05 = go.Figure(data=[go.Bar(x=xs_fig05, y=ys_fig05, orientation='v', text=ys_fig05,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45, texttemplate='%{text:.2f}')
                                     ])
            figs05.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolors, showgrid=False, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs05.update_yaxes(title_text='Mean Time Spent(hrs)', title_font_color=titlefontcolors, showgrid=True, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs05.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
            figs05.update_layout(title='Mean Time Spent to Complete(hrs)-Top 10', plot_bgcolor=plot_bgcolors)
            st.plotly_chart(figs05, use_container_width=True)

        with figs06, _lock:
            figs06 = go.Figure(data=[go.Bar(x=xs_fig06, y=ys_fig06, orientation='v', text=ys_fig06,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45, texttemplate='%{text:.2f}')
                                     ])
            figs06.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolors, showgrid=False, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs06.update_yaxes(title_text='Total Time Spent(hrs)', title_font_color=titlefontcolors, showgrid=True, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs06.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
            figs06.update_layout(title='Total Time Spent to Complete(hrs)-Top 10', plot_bgcolor=plot_bgcolors)
            st.plotly_chart(figs06, use_container_width=True)


#------------------------------------Number of schedule vs people --------------------------------------
        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_schedules_Technician, unsafe_allow_html=True)
        st.markdown('##')

        x_schedulepeople = dfs_completed.Attended_By.value_counts().index
        y_schedulepeople = dfs_completed.Attended_By.value_counts().values

        # y_faultpeople_sum = sum(y_faultpeople)
        # st.markdown(f"Total Fault = {y_faultpeople_sum}")

        fig_schedulepeople, fig_empty = st.columns(2)

        with fig_schedulepeople, _lock:
            fig_schedulepeople = go.Figure(data=[go.Bar(x=x_schedulepeople, y=y_schedulepeople, orientation='v', text=y_schedulepeople,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45)])
            fig_schedulepeople.update_xaxes(title_text="Name", title_font_color=titlefontcolors, showgrid=False, gridwidth=gridwidths,
                                gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis, tickangle=-45)
            fig_schedulepeople.update_yaxes(title_text='Number of Schedule', title_font_color=titlefontcolors, showgrid=False,
                                gridwidth=gridwidths, gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            fig_schedulepeople.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
            fig_schedulepeople.update_layout(title='Number of Schedule vs Name', plot_bgcolor=plot_bgcolors)
            st.plotly_chart(fig_schedulepeople, use_container_width=True)
        
        with fig_empty, _lock:
            st.empty()






elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')


# if st.session_state['authentication_status']:
#     st.write('Welcome *%s*' % (st.session_state['name']))
# elif st.session_state['authentication_status'] == False:
#     st.error('Username/password is incorrect')
# # elif st.session_state['authentication_status'] == None:
# #     st.warning('Please enter your username and password')




hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)
