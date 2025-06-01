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
            byte[] data = udpClient.Receive(ref remoteEP);

            try
            {
                using var ms = new MemoryStream(data);
                using Image<Rgba32> image = Image.Load<Rgba32>(ms);

                string filename = $"received_{DateTime.Now:HHmmssfff}.jpg";
                image.Save(filename);
                Console.WriteLine($"Image saved: {filename}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"Error decoding image: {e.Message}");
            }
        }
    }
}
