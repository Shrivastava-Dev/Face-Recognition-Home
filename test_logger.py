from logger import log_event, load_logs

log_event("face_recognized", name="Aditya")
log_event("new_registration", name="Rahul")
log_event("face_recognized", name="Rahul")

logs = load_logs()
for log in logs:
    print(log)