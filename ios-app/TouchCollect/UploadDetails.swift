//
//  UploadDetails.swift
//  TouchCollect
//
//  Created by Henry on 13/02/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import UIKit
import Alamofire

class UploadDetails: UIViewController {
    
    var activityIndicator: UIActivityIndicatorView = UIActivityIndicatorView()
    var height: String = ""
    var gender: String = ""
    var hand: String = ""
    var country: String = ""
    var weight: String = ""
    var day: String = ""
    var month: String = ""
    var year: String = ""

    override func viewDidLoad() {
        super.viewDidLoad()
        
        self.title = "Upload"
        self.navigationItem.hidesBackButton = true
        
        activityIndicator.center = self.view.center
        activityIndicator.hidesWhenStopped = true
        activityIndicator.style = .large
        view.addSubview(activityIndicator)
        activityIndicator.startAnimating()
        
        let defaults = UserDefaults.standard
        var push_token = defaults.string(forKey: "push_token")
        
        if (push_token == nil) {
            push_token = ""
        }
        
        let parameters: Parameters = [
            "phone_model": String(UIDevice.modelName),
            "country": country,
            "gender": gender,
            "handedness": hand,
            "height": Int(height)!,
            "weight": Int(weight)!,
            "doby": Int(year)!,
            "dobm": Int(month)!,
            "dobd": Int(day)!,
            "timezone": String(TimeZone.current.identifier),
            "push_token": push_token
        ]
        
        print(parameters)

        AF.request("https://ssloxford.co.uk:8009/enrol", method: .post, parameters: parameters, encoding: JSONEncoding.default).validate(statusCode: 200..<300).responseJSON { response in
            print(response)
            switch(response.result) {
            case .success(let JSON):
                let resp = JSON as! NSDictionary
                let uuid = resp.object(forKey: "uuid")!
                let mturk_token = resp.object(forKey: "mturk_token")!
                
                let defaults = UserDefaults.standard
                defaults.set(uuid, forKey: "uuid")
                defaults.set(mturk_token, forKey: "mturk_token")
                defaults.set(true, forKey: "enrolled")
                
                defaults.set(false, forKey: "done_article")
                defaults.set(false, forKey: "done_image")
                defaults.set(false, forKey: "shown_turk")

                let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
                let startViewController = storyBoard.instantiateViewController(withIdentifier: "Start") as! Start
                
                startViewController.showPopup = true
                self.navigationController?.pushViewController(startViewController, animated: true)
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
    }
}
