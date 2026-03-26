import pywhatkit

def send_prediction_alert(
    phone_number: str, 
    sim_cpu: int, 
    sim_mem: int, 
    sim_net: float, 
    action_title: str, 
    action_desc: str
):
    """
    Formats the prediction alert into a formal WhatsApp message and sends it via PyWhatKit.
    """
    
    wa_message = (
        f"🌍 *Eco-Scale Alert*\n\n"
        f"📊 *Live Telemetry:*\n"
        f"• CPU Load: {sim_cpu}%\n"
        f"• Mem Load: {sim_mem}%\n"
        f"• Network Traffic: {sim_net} Gbps\n\n"
        f"✅ *Predicted Action:*\n"
        f"_{action_title}_\n{action_desc}\n\n"
        f"🤖 _Powered by the Eco-Scale Random Forest Classifier_"
    )
    
    # PyWhatKit requires the phone number string to be exactly standard E.164 (+CountryCode...)
    clean_num = phone_number if phone_number.startswith('+') else f"+{phone_number}"
    
    # Send instantly without closing the newly opened tab
    pywhatkit.sendwhatmsg_instantly(
        phone_no=clean_num, 
        message=wa_message, 
        wait_time=15, 
        tab_close=False
    )
