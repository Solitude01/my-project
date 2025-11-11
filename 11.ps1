# 每 0.2 秒发送一次 ping
while ($true) {
    ping 10.30.43.199 -n 1
    Start-Sleep -Milliseconds 200
}
