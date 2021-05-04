//
//  Upload.swift
//  TouchCollect
//
//  Created by Henry on 27/01/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import UIKit
import Alamofire

class Upload: UIViewController {
    
    @IBOutlet weak var lUpload: UILabel!
    var activityIndicator: UIActivityIndicatorView = UIActivityIndicatorView()
    var game = ""
    
    @IBOutlet weak var bRetry: UIButton!
    var iterationArticleData: [[String: Any]] = []
    var iterationImageData: [[String: Any]] = []
    
    var sGyro: String = ""
    var sAcc: String = ""
    var sTouch: String = ""
    
    let debug = false
    var data: [[String: Any]] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        
        self.title = "Upload"
        self.navigationItem.hidesBackButton = true

        activityIndicator.center = self.view.center
        activityIndicator.hidesWhenStopped = true
        activityIndicator.style = .large
        
        view.addSubview(activityIndicator)
        activityIndicator.startAnimating()
        
        bRetry.contentEdgeInsets = UIEdgeInsets(top: 10.0, left: 30.0, bottom: 10.0, right: 30.0)
        bRetry.layer.cornerRadius = 20
        
        data = [
            [
                "game": "scroll",
                "iteration": iterationArticleData
            ],
            [
                "game": "swipe",
                "iteration": iterationImageData
            ]
        ]
        
        if (debug) {
            let alert = UIAlertController(title: "Manual UID", message: "", preferredStyle: .alert)
             alert.addTextField { (textField) in
                 textField.text = ""
             }

             alert.addAction(UIAlertAction(title: "Submit", style: .default, handler: { [weak alert] (_) in
                let textField = alert!.textFields![0] // Force unwrapping because we know it exists.
                
                let defaults = UserDefaults.standard
                let parameters: Parameters = [
                    "uuid": defaults.string(forKey: "uuid")!,
                    "manual_id": textField.text!,
                    "data": self.data
                ]
                
                print(parameters)
                
                AF.request("https://ssloxford.co.uk:8009/measurement", method: .post, parameters: parameters, encoding: JSONEncoding.default).validate(statusCode: 200..<300).responseJSON { response in
                    print(response)
                    switch(response.result) {
                    case .success(let JSON):
                        let resp = JSON as! NSDictionary
                        print(resp)
                        
                        let defaults = UserDefaults.standard
                         
                         
                        if (!defaults.bool(forKey: "shown_turk")){
                            defaults.set(true, forKey: "shown_turk")
                         
                            let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
                            let startViewController = storyBoard.instantiateViewController(withIdentifier: "Final") as! Final
                                                        
                            self.navigationController?.pushViewController(startViewController, animated: true)
                        } else {
                            let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
                            let startViewController = storyBoard.instantiateViewController(withIdentifier: "Start") as! Start
                            
                            startViewController.showMoney = true

                            self.navigationController?.pushViewController(startViewController, animated: true)
                        }


                    case .failure(_):
                        if let data = response.data {
                            if let errorString = String(bytes: data, encoding: .utf8) {
                                print(errorString)
                            }
                        }
                        
                        var alertController: UIAlertController
                        alertController = UIAlertController(title: "Issue communicating with server, please try again later", message: "", preferredStyle: .alert)
                        alertController.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(alertController, animated: false)
                        
                    }
                }
             }))
            
            self.present(alert, animated: false)
        } else {
            let defaults = UserDefaults.standard
            let parameters: Parameters = [
                "uuid": defaults.string(forKey: "uuid")!,
                "data": data
            ]
            
            print(parameters)


            AF.request("https://ssloxford.co.uk:8009/measurement", method: .post, parameters: parameters, encoding: JSONEncoding.default).validate(statusCode: 200..<300).responseJSON { response in
                print(response)
                switch(response.result) {
                case .success(let JSON):
                    let resp = JSON as! NSDictionary
                    print(resp)
                    
                    let defaults = UserDefaults.standard
                     
                     
                    if (!defaults.bool(forKey: "shown_turk")){
                        defaults.set(true, forKey: "shown_turk")
                     
                        let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
                        let startViewController = storyBoard.instantiateViewController(withIdentifier: "Final") as! Final
                                                    
                        self.navigationController?.pushViewController(startViewController, animated: true)
                    } else {
                        let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
                        let startViewController = storyBoard.instantiateViewController(withIdentifier: "Start") as! Start
                        
                        startViewController.showMoney = true

                        self.navigationController?.pushViewController(startViewController, animated: true)
                    }


                case .failure(_):
                    if let data = response.data {
                        if let errorString = String(bytes: data, encoding: .utf8) {
                            print(errorString)
                        }
                    }
                    
                    self.bRetry.isHidden = false;
                    self.activityIndicator.isHidden = true;
                    self.lUpload.isHidden = true;
                    
                    var alertController: UIAlertController
                    alertController = UIAlertController(title: "Issue communicating with server, please try again later", message: "", preferredStyle: .alert)
                    alertController.addAction(UIAlertAction(title: "OK", style: .default))
                    self.present(alertController, animated: false)
                    
                }
            }
        }

    }
    
    @IBAction func retrySubmit(_ sender: Any) {
        self.bRetry.isHidden = true;
        self.activityIndicator.isHidden = false;
        self.lUpload.isHidden = false;
        
        let defaults = UserDefaults.standard
        let parameters: Parameters = [
            "uuid": defaults.string(forKey: "uuid")!,
            "data": data
        ]
        
        print(parameters)


        AF.request("https://ssloxford.co.uk:8009/measurement", method: .post, parameters: parameters, encoding: JSONEncoding.default).validate(statusCode: 200..<300).responseJSON { response in
            print(response)
            switch(response.result) {
            case .success(let JSON):
                let resp = JSON as! NSDictionary
                print(resp)
                
                let defaults = UserDefaults.standard
                 
                 
                if (!defaults.bool(forKey: "shown_turk")){
                    defaults.set(true, forKey: "shown_turk")
                 
                    let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
                    let startViewController = storyBoard.instantiateViewController(withIdentifier: "Final") as! Final
                                                
                    self.navigationController?.pushViewController(startViewController, animated: true)
                } else {
                    let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
                    let startViewController = storyBoard.instantiateViewController(withIdentifier: "Start") as! Start
                    
                    startViewController.showMoney = true

                    self.navigationController?.pushViewController(startViewController, animated: true)
                }


            case .failure(_):
                if let data = response.data {
                    if let errorString = String(bytes: data, encoding: .utf8) {
                        print(errorString)
                    }
                }
                                
                var alertController: UIAlertController
                alertController = UIAlertController(title: "Issue communicating with server, please try again later", message: "", preferredStyle: .alert)
                alertController.addAction(UIAlertAction(title: "OK", style: .default))
                self.present(alertController, animated: false)
                
                self.bRetry.isHidden = false;
                self.activityIndicator.isHidden = true;
                self.lUpload.isHidden = true;
                
            }
        }
    }
}
