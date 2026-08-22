import threading
import pydivert

TLS_HANDSHAKE = b"\x16\x03"

class DpiEngine:
    def __init__(self, split_pos: int = 2, fake_ttl: int = 3):
        self.split_pos = split_pos
        self.fake_ttl = fake_ttl
        self.running = False
        self.filter_rule = (
            "outbound and tcp.PayloadLength > 0 and "
            "(tcp.DstPort == 80 or tcp.DstPort == 443 or tcp.DstPort == 8443 or tcp.DstPort == 5222)"
        )

    def is_tls_client_hello(self, payload: bytes) -> bool:
        return len(payload) > 5 and payload.startswith(TLS_HANDSHAKE)

    def start(self):
        self.running = True
        try:
            with pydivert.WinDivert(self.filter_rule) as w:
                while self.running:
                    try:
                        packet = w.recv(timeout=1000)
                        if packet is None:
                            continue

                        payload = packet.payload
                        if self.is_tls_client_hello(payload):
                            fake_packet = packet
                            fake_packet.ipv4.ttl = self.fake_ttl
                            fake_packet.payload = b"\x16\x03\x01\x00\x05\x01\x00\x00\x01\x00"
                            w.send(fake_packet)

                            p1 = packet
                            p1.payload = payload[:self.split_pos]
                            w.send(p1)

                            p2 = packet
                            p2.tcp.seq_num += len(p1.payload)
                            p2.payload = payload[self.split_pos:]
                            w.send(p2)
                            continue

                        w.send(packet)
                    except Exception:
                        continue
        except Exception as e:
            print(f"[!] Ошибка WinDivert: {e}")

    def stop(self):
        self.running = False
