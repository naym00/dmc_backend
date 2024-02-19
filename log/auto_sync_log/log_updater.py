from apscheduler.schedulers.background import BackgroundScheduler
from log.views import auto_save


scheduler_running = False
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(auto_save,"interval", minutes=60,id="log_002",replace_existing=True)
    scheduler.start()
    global scheduler_running

    # Check if the scheduler is already running
    if scheduler_running:
        print("Scheduler is already running.")
        scheduler.remove_all_jobs()

        return

    # Start the scheduler
    scheduler.start()
    scheduler_running = True

    print("Scheduler started.")

    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        # Shut down the scheduler gracefully when the script is interrupted
        scheduler.shutdown()
        scheduler_running = False

