using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// for Live2D model
using Live2D.Cubism.Core;
using Live2D.Cubism.Framework;

// socket
using System;
using System.Threading;
using System.Net;
using System.Net.Sockets;
using System.Text;

public class NatoriController : MonoBehaviour
{

    private CubismModel model;

    // threshold to activate changes in whole model's x/z parameter
    // instead of just changes in head
    public float abs_body_roll_threshold = 30;
    public float abs_body_yaw_threshold = 30;
    public float abs_body_roll_yaw_max = 60;

    public float ear_max_threshold = 0.38f;
    public float ear_min_threshold = 0.30f;

    public float iris_left_ceiling = 0.2f;
    public float iris_right_ceiling = 0.85f;
    public float iris_up_ceiling = 0.8f;
    public float iris_down_ceiling = 0.2f;

    public float mar_max_threshold = 1.0f;
    public float mar_min_threshold = 0.0f;

    public bool change_mouth_form = false;
    public float mouth_dist_min = 60.0f;
    public float mouth_dist_max = 80.0f;





    // Thread receiveThread;
    // TcpClient client;
    // TcpListener listener;
    // int port = 5066;

    private float t1;       // for breath
    private float roll = 0, pitch = 0, yaw = 0;
    private float ear_left = 0, ear_right = 0;
    private float x_ratio_left = 0, y_ratio_left = 0, x_ratio_right = 0, y_ratio_right = 0;
    private float mar = 0, mouth_dist = 0;
    private float shoudler_l_rotaton = 0;
    private float shoudler_r_rotaton = 0;
    private float elbow_l_rotaton = 0;
    private float elbow_r_rotaton = 0;
    private float wrist_l_rotaton = 0;
    private float wrist_r_rotaton = 0;

    private bool blush = false;

    // Start is called before the first frame update
    void Start()
    {
        model = this.FindCubismModel();

        abs_body_roll_threshold = Mathf.Abs(abs_body_roll_threshold);
        abs_body_yaw_threshold = Mathf.Abs(abs_body_yaw_threshold);
        abs_body_roll_yaw_max = Mathf.Abs(abs_body_roll_yaw_max);

        // InitTCP();

        // create a Tag namely "GameController" and attach it to an empty GameObject
        // with the script "UISystem.cs" on it
        // Load saved JSON data at start
        //GameObject.FindWithTag("GameController").GetComponent<UISystem>().LoadData();
        //GameObject.FindWithTag("GameController").GetComponent<UISystem>().InitUI();

    }

    // // Launch TCP to receive message from python
    // public void InitTCP() {
    //     receiveThread = new Thread(new ThreadStart(ReceiveData));
    //     receiveThread.IsBackground = true;
    //     receiveThread.Start();
    // }

    // // close TCP connection from unity
    // public void stopTCP() {
    //     if (listener != null) {
    //         if (client != null)
    //             client.Close();
    //         listener.Stop();
    //     }
    // }

    // private void ReceiveData() {
    //     try {
    //         listener = new TcpListener(IPAddress.Parse("127.0.0.1"), port);
    //         // listener = new TcpListener(IPAddress.Parse("192.168.0.107"), port);
    //         listener.Start();
    //         Byte[] bytes = new Byte[1024];

    //         while (true) {
    //             using(client = listener.AcceptTcpClient()) {
    //                 using (NetworkStream stream = client.GetStream()) {
    //                     int length;
    //                     while ((length = stream.Read(bytes, 0, bytes.Length)) != 0) {
    //                         var incommingData = new byte[length];
    //                         Array.Copy(bytes, 0, incommingData, 0, length);
    //                         string clientMessage = Encoding.ASCII.GetString(incommingData);
    //                         string[] res = clientMessage.Split(' ');

    //                         roll = float.Parse(res[0]);
    //                         pitch = float.Parse(res[1]);
    //                         yaw = float.Parse(res[2]);
    //                         ear_left = float.Parse(res[3]);
    //                         ear_right = float.Parse(res[4]);
    //                         x_ratio_left = float.Parse(res[5]);
    //                         y_ratio_left = float.Parse(res[6]);
    //                         x_ratio_right = float.Parse(res[7]);
    //                         y_ratio_right = float.Parse(res[8]);
    //                         mar = float.Parse(res[9]);
    //                         mouth_dist = float.Parse(res[10]);
    //                     }
    //                 }
    //             }
    //         }
    //     } catch(Exception e) {
    //         print(e.ToString());
    //     }
    // }

    public void parseMessage(String message)
    {
        string[] res = message.Split(' ');

        roll = float.Parse(res[0]);
        pitch = float.Parse(res[1]);
        yaw = float.Parse(res[2]);
        ear_left = float.Parse(res[3]);
        ear_right = float.Parse(res[4]);
        x_ratio_left = float.Parse(res[5]);
        y_ratio_left = float.Parse(res[6]);
        x_ratio_right = float.Parse(res[7]);
        y_ratio_right = float.Parse(res[8]);
        mar = float.Parse(res[9]);
        mouth_dist = float.Parse(res[10]);
        shoudler_l_rotaton = float.Parse(res[11]);
        elbow_l_rotaton = float.Parse(res[12]);
        wrist_l_rotaton = float.Parse(res[13]);
        shoudler_r_rotaton = float.Parse(res[14]);
        elbow_r_rotaton = float.Parse(res[15]);
        wrist_r_rotaton = float.Parse(res[16]);

    }

    // Update is called once per frame
    void Update()
    {
        print(string.Format("Roll: {0:F}; Pitch: {1:F}; Yaw: {2:F}", roll, pitch, yaw));

        // control the blush of the avatar
        if (Input.GetKeyDown(KeyCode.Alpha1))
        {
            if (blush == false)
                blush = true;
            else
                blush = false;
        }
    }

    // Apply all changes of control variables here~
    // https://docs.live2d.com/cubism-sdk-tutorials/about-parameterupdating-of-model/?locale=en_us
    // Tip 1
    void LateUpdate()
    {
        // yaw
        var parameter = model.Parameters[0];
        parameter.Value = -Mathf.Clamp(yaw, -30, 30);

        // pitch
        parameter = model.Parameters[1];
        parameter.Value = Mathf.Clamp(pitch, -30, 30);

        // roll
        parameter = model.Parameters[2];
        parameter.Value = -Mathf.Clamp(roll, -30, 30);

        // breath
        t1 += Time.deltaTime;
        float value = (Mathf.Sin(t1 * 3f) + 1) * 0.5f;
        parameter = model.Parameters[23];
        parameter.Value = value;

        if (blush)
        {
            parameter = model.Parameters[3];
            parameter.Value = 1;
        }
        else
        {
            parameter = model.Parameters[3];
            parameter.Value = 0;
        }

        EyeBlinking();

        IrisMovement();

        MouthOpening();

        ArmMove();

        BodyMovement();
        if (change_mouth_form)
            MouthForm();
        
    }

    // whole body movement (body X/Z)
    // optional as the effect is not that pronounced
    void BodyMovement()
    {
        // roll
        var parameter = model.Parameters[22];
        if (Mathf.Abs(roll) > abs_body_roll_threshold)
        {
            parameter.Value = -(10 - 0) / (abs_body_roll_yaw_max - abs_body_roll_threshold) * ((Mathf.Abs(roll) - abs_body_roll_threshold) * Mathf.Sign(roll));
        }
        else
        {
            parameter.Value = 0;
        }

        // yaw
        parameter = model.Parameters[20];
        if (Mathf.Abs(yaw) > abs_body_yaw_threshold)
        {
            parameter.Value = -(10 - 0) / (abs_body_roll_yaw_max - abs_body_yaw_threshold) * ((Mathf.Abs(yaw) - abs_body_yaw_threshold) * Mathf.Sign(yaw));
        }
        else
        {
            parameter = model.Parameters[20];
            parameter.Value = 0;
        }
    }

    void EyeBlinking()
    {
        // my left eye = live2d's right (mirroring)
        ear_left = Mathf.Clamp(ear_left, ear_min_threshold, ear_max_threshold);
        float eye_L_value = (ear_left - ear_min_threshold) / (ear_max_threshold - ear_min_threshold) * 1;
        var parameter = model.Parameters[6];
        parameter.Value = eye_L_value;

        // my right eye = live2d's left (mirroring)
        ear_right = Mathf.Clamp(ear_right, ear_min_threshold, ear_max_threshold);
        float eye_R_value = (ear_right - ear_min_threshold) / (ear_max_threshold - ear_min_threshold) * 1;
        parameter = model.Parameters[3];
        parameter.Value = eye_R_value;
    }

    void IrisMovement()
    {
        float eyeball_x = (x_ratio_left + x_ratio_right) / 2;
        float eyeball_y = (y_ratio_left + y_ratio_right) / 2;

        eyeball_x = Mathf.Clamp(eyeball_x, iris_left_ceiling, iris_right_ceiling);
        eyeball_y = Mathf.Clamp(eyeball_y, iris_down_ceiling, iris_up_ceiling);

        // range is [-1, 1]
        eyeball_x = (eyeball_x - iris_left_ceiling) / (iris_right_ceiling - iris_left_ceiling) * 2 - 1;
        eyeball_y = (eyeball_y - iris_down_ceiling) / (iris_up_ceiling - iris_down_ceiling) * 2 - 1;

        // optional
        // pass the value to an "activation function"
        // to create a smoother effect (when the iris is near center)
        // eyeball_x = Mathf.Pow(eyeball_x, 3);
        // eyeball_y = Mathf.Pow(eyeball_y, 3);

        var parameter = model.Parameters[8];
        parameter.Value = eyeball_x;
        parameter = model.Parameters[9];
        parameter.Value = eyeball_y;
    }

    void MouthOpening()
    {
        // mouth aspect ratio -> mouth opening
        float mar_clamped = Mathf.Clamp(mar, mar_min_threshold, mar_max_threshold);
        mar_clamped = (mar_clamped - mar_min_threshold) / (mar_max_threshold - mar_min_threshold) * 1;
        var parameter = model.Parameters[23];
        parameter.Value = mar_clamped;
    }

    void MouthForm()
    {
        // mouth distance -> mouth form
        float mouth_dist_clamped = Mathf.Clamp(mouth_dist, mouth_dist_min, mouth_dist_max);
        // range is [-1, 1]
        mouth_dist_clamped = (mouth_dist_clamped - mouth_dist_min) / (mouth_dist_max - mouth_dist_min) * 2 - 1;
        var parameter = model.Parameters[22];
        parameter.Value = mouth_dist_clamped;

    }

    void ArmMove()
    {
        var parameter1 = model.Parameters[62];
        Debug.Log(elbow_r_rotaton);
        parameter1.Value = Mathf.Clamp(elbow_r_rotaton / 1000f, -40, 10);
        //Mathf.Clamp(180-elbow_l_rotaton/7.5f,-40,10);

        var parameter = model.Parameters[61];
        parameter.Value = Mathf.Clamp(shoudler_r_rotaton / 9 - 10, 5, 30);



        var parameter2 = model.Parameters[63];
        parameter2.Value = Mathf.Clamp(wrist_r_rotaton / 6 - 30, -30, 30);

       // parameter = model.Parameters[6];
        //parameter.Value = Mathf.Clamp(shoudler_l_rotaton / 9 - 10, 5, 30);

      
    }



    // void OnApplicationQuit()
    // {
    //     // close the thread when the application quits
    //     receiveThread.Abort();
    // }


}
