import subprocess

def push_media_to_device(udid: str, local_file_path: str, remote_file_name: str = 'affiliate_vid.mp4') -> str:
    """
    Push an MP4 media file from the server to the physical Android device's DCIM
    folder and force a media scan so it shows up in the gallery picker.
    
    Args:
        udid: The device ADB UDID.
        local_file_path: Absolute or relative path to the MP4 file.
        remote_file_name: The filename to save as on the device.
        
    Returns:
        The remote path where the file was written.
    """
    remote_path = f'/sdcard/DCIM/Camera/{remote_file_name}'
    
    print(f"Bắt đầu đẩy file media {local_file_path} lên thiết bị {udid}...")
    
    # 1. ADB Push file
    push_cmd = ['adb', '-s', udid, 'push', local_file_path, remote_path]
    subprocess.run(push_cmd, check=True)
    
    # 2. ADB Shell Broadcast scan
    # This is critical so Facebook's custom photo picker can instantly see the new Reel.
    scan_cmd = [
        'adb', '-s', udid, 'shell', 'am', 'broadcast', 
        '-a', 'android.intent.action.MEDIA_SCANNER_SCAN_FILE', 
        '-d', f'file://{remote_path}'
    ]
    subprocess.run(scan_cmd, check=True)
    
    print(f"Đã cập nhật media thành công vào thư viện thiết bị tại {remote_path}")
    return remote_path
