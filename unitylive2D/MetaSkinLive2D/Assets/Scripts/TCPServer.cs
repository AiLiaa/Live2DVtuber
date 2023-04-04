using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

// Socket
using System;
using System.Threading;
using System.Net;
using System.Net.Sockets;
using System.Text;

public class TCPServer : MonoBehaviour
{
    // the controller script attached to the live2d / 3D model
    HiyoriController hiyoriController;
    NatoriController natoriController;

    Thread receiveThread;

    // the client connected to the TCP server
    TcpClient client;

    // Unity side
    TcpListener server;

    bool serverUp = false;

    [SerializeField]
    int port = 5066;
    int portMin = 5000;
    int portMax = 6000;

    // UI related
    public Button startTCPBtn;
    public Button stopTCPBtn;
    public InputField portInputField;
    public Button confirmPortBtn;
    public Text portLogText;

    // Start is called before the first frame update
    void Start()
    {
        // Attach a Tag "Player" on the Live2D model
        hiyoriController = GameObject.FindWithTag("Player").GetComponent<HiyoriController>();
        natoriController = GameObject.FindWithTag("Player").GetComponent<NatoriController>();

        //SetUIInteractables();

        //portInputField.text = String.Format("{0}", port);
        //portLogText.text = String.Format("Port Range: {0} - {1}", portMin, portMax);
        InitTCP();
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    // Init the TCP server
    // Attach this to the OnClick listener of Start button on TCP UI panel
    public void InitTCP() {
        try {
            // local host
            server = new TcpListener(IPAddress.Parse("127.0.0.1"), port);
            server.Start();

            serverUp = true;

            // create a thread to accept client
            receiveThread = new Thread(new ThreadStart(ReceiveData));
            receiveThread.IsBackground = true;
            receiveThread.Start();
        
        } catch(Exception e) {
            // usually error occurs if the port is used by other program.
            // a "SocketException: Address already in use" error will show up here
            print(e.ToString());
        }        
    }

    // Stop the TCP server
    // Attach this to the OnClick listener of Stop button on TCP UI panel
    public void StopTCP() {
        // close the client here?
        
        if (!serverUp) return;

        if (client != null) client.Close();

        server.Stop();

        print("Server is off.");

        if (receiveThread.IsAlive) receiveThread.Abort();

        serverUp = false;
    }

    private void ReceiveData() {
        try {
            // Buffer
            Byte[] bytes = new Byte[1024];

            while(true) {
                print("Waiting for a connection...");

                client = server.AcceptTcpClient();
                print("Connected!");

                // I/O Stream for sending/ receiving to/ from client
                NetworkStream stream = client.GetStream();

                int length;

                 while ((length = stream.Read(bytes, 0, bytes.Length)) != 0) {
                    var incommingData = new byte[length];
                    Array.Copy(bytes, 0, incommingData, 0, length);
                    string clientMessage = Encoding.ASCII.GetString(incommingData);

                    // call Hiyori Controller to update values
                    hiyoriController.parseMessage(clientMessage);

                    print("Received message: " + clientMessage);

                    // SendData(client);

                }
            }
        }
        catch(Exception e) {
            print(e.ToString());
        }
    }

    // reserved incase there is situation where we have to send data to python/unity side

    // private void SendData(TcpClient client) {

    //     // I/O Stream for sending/ receiving to/ from client
    //     NetworkStream stream = client.GetStream();

    //     string message = "Received message";
    //     byte[] msg = Encoding.ASCII.GetBytes(message);

    //     // sending data to client
    //     stream.Write(msg, 0, msg.Length);

    //     print("Received message is sent");
    // }

    // Control whether each button can be clicked or not.
    // Attach this to OnClick listener of both start and stop button
    public void SetUIInteractables() {
        startTCPBtn.interactable = !serverUp;
        stopTCPBtn.interactable = serverUp;

        portInputField.interactable = !serverUp;
        confirmPortBtn.interactable = !serverUp;
    }

    // Check whether the string contains only ascii numbers
    bool IsDigitsOnly(string str) {
        foreach (char c in str) {
            if (c < '0' || c > '9')
                return false;
        }
        return true;
    }

    // Confirm the port input from user
    // Attach this to the Confirm button next to the input field of port on TCP UI panel.
    public void ConfirmPort() {
        // get the input text from the input field
        string s = portInputField.text;

        // input check if there are non-numeric characters
        if (!(IsDigitsOnly(s))) {
            portLogText.text = "Port should an integer.";
            return;
        }

        // convert it to int and do range check
        int temp;
        bool success = Int32.TryParse(s, out temp);

        if (!success) {
            portLogText.text = "Number may be too large to parse to an integer";
        }

        // 1000 ports should be enough
        if (temp <= portMin || temp > portMax) {
            portLogText.text = String.Format("Port should be within the ramge: {0} - {1}", portMin, portMax);
            return;
        }

        port = temp;
        portLogText.text = String.Format("TCP port = {0}", port);
    }

    void OnApplicationQuit()
    {
        // close the TCP stuffs when the application quits
        StopTCP();
    }
}
