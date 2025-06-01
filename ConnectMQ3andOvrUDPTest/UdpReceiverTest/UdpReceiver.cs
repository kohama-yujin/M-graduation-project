// UdpReceiver.cs
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;

class UdpReceiver
{
    static void Main()
    {
        int listenPort = 12345; // 送信側と合わせる
        UdpClient udpClient = new UdpClient(listenPort);
        IPEndPoint remoteEP = new IPEndPoint(IPAddress.Any, 0);

        Console.WriteLine($"Listening on port {listenPort}...");

        while (true)
        {
            try
            {
                // 最初のメッセージでパケット数を取得
                byte[] headerBytes = udpClient.Receive(ref remoteEP);
                string headerString = Encoding.UTF8.GetString(headerBytes);
                int packetCount = int.Parse(headerString);
                Console.WriteLine($"Expecting {packetCount} packets...");

                // 画像データを受信
                Dictionary<int, byte[]> packets = new Dictionary<int, byte[]>();

                for (int i = 0; i < packetCount; i++)
                {
                    byte[] data = udpClient.Receive(ref remoteEP);
                    // 先頭4バイトはパケット番号（ビッグエンディアン）
                    // C#ではリトルエンディアンを期待されるため、逆向きに格納
                    int seq = BitConverter.ToInt32(new byte[] { data[3], data[2], data[1], data[0] }, 0);
                    // 4バイト以降が画像データ
                    byte[] chunk = new byte[data.Length - 4];
                    Array.Copy(data, 4, chunk, 0, chunk.Length);
                    // パケット番号順に格納
                    packets[seq] = chunk;
                }

                // 並べ替えて結合
                List<byte> imageBytes = new List<byte>();
                for (int i = 0; i < packetCount; i++)
                {
                    imageBytes.AddRange(packets[i]);
                }
                using var ms = new MemoryStream(imageBytes.ToArray());
                using Image image = Image.Load(ms);  // 自動でJPEGデコード


                // 保存 or 表示（ここでは保存）
                string outputPath = $"../output/received_{DateTime.Now.Ticks}.jpg";
                image.Save(outputPath);
                Console.WriteLine($"Saved {outputPath}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"Error decoding image: {e.Message}");
            }
        }
    }
}