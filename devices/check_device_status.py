from pythonping import ping

def is_device_active(ip_address):
    try:
        result = ping(ip_address, count=2)
        return result.success()
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Example usage
ip_to_check = "10.10.20.52"
result = is_device_active(ip_to_check)

if result:
    print(f"The device at {ip_to_check} is active.")
else:
    print(f"The device at {ip_to_check} is not active.")
