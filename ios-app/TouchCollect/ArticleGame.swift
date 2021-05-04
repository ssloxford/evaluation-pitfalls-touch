//
//  ArticleGame.swift
//  TouchCollect
//
//  Created by Henry on 27/01/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import UIKit
import CoreMotion

class ATTableView: UITableView, UIGestureRecognizerDelegate {
    func gestureRecognizer(_ gestureRecognizer: UIGestureRecognizer,
                           shouldRecognizeSimultaneouslyWith otherGestureRecognizer: UIGestureRecognizer) -> Bool {
        return true
    }
}

class ArticleGame: UITableViewController {
    var articleData: [ArticleData] = []
    var cells: [ArticleGameCell] = []
    var motion = CMMotionManager()
    var answer = 0
    var correct = 0
    var goal = 5
    var total = 20
    var iterationCount = 0
    var swipes = 0

    var gyroscopeData: [[String: Any]] = []
    var accelData: [[String: Any]] = []
    var touchData: [[String: Any]] = []
    
    var iterationArticleData: [[String: Any]] = []
    var iterationImageData: [[String: Any]] = []


    override func viewDidLoad() {
        super.viewDidLoad()
        self.navigationItem.hidesBackButton = true
        
        setupGame()
        setupSensors()
    }
    
    func setupGame() {
        answer = Int.random(in: 0 ..< total)

        articleData = getFeed()
        tableView.reloadData()
        tableView.scrollToRow(at: IndexPath(row: 0, section: 0), at: .top, animated: false)

        if let navigationBar = self.navigationController?.navigationBar {
            for view in navigationBar.subviews {
                view.removeFromSuperview()
            }
            
            let firstFrame = CGRect(x: 10, y: 0, width: navigationBar.frame.width-80, height: navigationBar.frame.height)
            let secondFrame = CGRect(x: navigationBar.frame.width-60, y: 0, width: 60, height: navigationBar.frame.height)

            let firstLabel = UILabel(frame: firstFrame)
            firstLabel.text = articleData[answer].question
            firstLabel.numberOfLines = 10
            firstLabel.font = UIFont.boldSystemFont(ofSize: 15.0)
            firstLabel.textColor = UIColor.white

            let secondLabel = UILabel(frame: secondFrame)
            secondLabel.text = "Correct \(correct)/\(goal)"
            secondLabel.font = UIFont.systemFont(ofSize: 16.0)
            secondLabel.numberOfLines = 2
            secondLabel.textAlignment = .center
            secondLabel.textColor = UIColor.white

            navigationBar.addSubview(firstLabel)
            navigationBar.addSubview(secondLabel)
        }
    }
    
    func setupSensors(){
        motion.startAccelerometerUpdates(to: OperationQueue.current!) { (data,error) in
            if let trueData = data {
                self.view.reloadInputViews()
                let x = trueData.acceleration.x
                let y = trueData.acceleration.y
                let z = trueData.acceleration.z
                
                self.accelData.append(
                    [
                        "timestamp": Date().timeIntervalSince1970 * 1000,
                        "x": x,
                        "y": y,
                        "z": z
                    ]
                )
            }
        }
        
        motion.startGyroUpdates(to: OperationQueue.current!) { (data,error) in
            if let trueData = data {
                self.view.reloadInputViews()
                let x = trueData.rotationRate.x
                let y = trueData.rotationRate.y
                let z = trueData.rotationRate.z
               
                self.gyroscopeData.append(
                    [
                        "timestamp": Date().timeIntervalSince1970 * 1000,
                        "x": x,
                        "y": y,
                        "z": z
                    ]
                )
            }
        }
    }
    
    @IBAction func handlePan(_ recognizer: ImmediatePanG) {
     
        let location = recognizer.location(in: view.superview)
        let time = Date().timeIntervalSince1970 * 1000
         
         switch recognizer.state {
         case .began:
             //print("STARTED")
             touchData.append(
                 [
                     "timestamp": time,
                     "x": Double(location.x),
                     "y": Double(location.y),
                     "pressure": Double(recognizer.force),
                     "type": 0,
                     "area": Double(recognizer.area)
                 ]
             )

             print(time,Double(location.x),Double(location.y),Double(recognizer.force),Double(recognizer.area))
             break
         case .changed:
            touchData.append(
               [
                   "timestamp": time,
                   "x": Double(location.x),
                   "y": Double(location.y),
                   "pressure": Double(recognizer.force),
                   "type": 1,
                   "area": Double(recognizer.area)
               ]
            )
            print(time,Double(location.x),Double(location.y),Double(recognizer.force),Double(recognizer.area))
            break
         case .ended:
            touchData.append(
                [
                    "timestamp": time,
                    "x": Double(location.x),
                    "y": Double(location.y),
                    "pressure": Double(recognizer.force),
                    "type": 2,
                    "area": Double(recognizer.area)
                ]
            )
            
            swipes += 1

            print(time,Double(location.x),Double(location.y),Double(recognizer.force),Double(recognizer.area))
            //print("ENDED")
            break
         default:
             break
         }
    }
   
   func getFeed() -> [ArticleData]{
        let possibleTimeValue = ["seconds", "minutes", "hours", "days"]
        let possibleUValue = [["Jackson Sims", "u1"],["Christofer Forbes", "u2"],["Caitlyn Piper", "u3"],["Garry Prince", "u4"],["Elin Blackwell", "u5"],["Elvis Howard", "u6"],["Gerrard Green", "u7"]]
        var tmp: [ArticleData] = []
        var entries: [Int] = []
        var i = 0
         
        while (i < total) {
            let entry = Int.random(in: 0 ..< articleStruct.count)
            
            if (!entries.contains(entry)){
                entries.append(entry)
                i+=1
            }
        }

        for e in entries {
            let timePassed = Int.random(in: 2 ..< 25)
            let timeValue = Int.random(in: 0 ..< 4)
            let commentValue = Int.random(in: 0 ..< 101)
            let likesValue = Int.random(in: 0 ..< 501)
            let uValue = Int.random(in: 0 ..< 7)
        
            let time = possibleTimeValue[timeValue]
            let userName = possibleUValue[uValue][0]
            let userImage = possibleUValue[uValue][1]
            
            tmp.append(ArticleData(id: articleStruct[e].id, iUser: UIImage(named: userImage)!, iPost: UIImage(named: articleStruct[e].iPost)!, title: articleStruct[e].title, username: userName, post: articleStruct[e].post, isImagePost: articleStruct[e].isImagePost, timePassed: "Posted \(timePassed) \(time) ago", comments: "\(commentValue) comments", likes: "\(likesValue)", question: articleStruct[e].question))
        }
    
        return tmp
   }
   
   override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
       return articleData.count
   }
    
    override func tableView(_ tableView: UITableView, heightForRowAt indexPath: IndexPath) -> CGFloat {
        return UITableView.automaticDimension
    }
   
        
   override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {

           let articleRow = articleData[indexPath.row]
    
           let cell = tableView.dequeueReusableCell(withIdentifier: "ArticlesList", for: indexPath) as! ArticleGameCell
           cell.setArticle(article: articleRow)
           cell.selectionStyle = .none
    
           return cell
   }

   override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        var alertController: UIAlertController
    
//        accelData.append(
//            [
//                "timestamp": Date().timeIntervalSince1970 * 1000,
//                "x": 1,
//                "y": 2,
//                "z": 3
//            ]
//        )
//    
//        gyroscopeData.append(
//            [
//                "timestamp": Date().timeIntervalSince1970 * 1000,
//                "x": 1,
//                "y": 2,
//                "z": 3
//            ]
//        )
    
        iterationArticleData.append([
            "id": iterationCount,
            "touch": touchData,
            "accel": accelData,
            "gyro": gyroscopeData
        ])
    
        touchData = []
        accelData = []
        gyroscopeData = []

        iterationCount += 1
        
        if (indexPath.row == answer){
            correct += 1
            
            if (correct == goal) {
                print(swipes)

                for view in (self.navigationController?.navigationBar.subviews)! {
                     view.removeFromSuperview()
                }
                
                let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
                
                if (iterationImageData.isEmpty) {
                    var iamgeViewController: ImageGameInstructions

                    iamgeViewController = storyBoard.instantiateViewController(withIdentifier: "ImageGameInstructions") as! ImageGameInstructions
                    iamgeViewController.iterationArticleData = iterationArticleData
                    
                    iterationImageData = []
                    iterationArticleData = []

                    navigationController?.pushViewController(iamgeViewController, animated: true)
                } else {
                    var uploadViewController: Upload

                    uploadViewController = storyBoard.instantiateViewController(withIdentifier: "Upload") as! Upload

                    uploadViewController.iterationImageData = iterationImageData
                    uploadViewController.iterationArticleData = iterationArticleData
                    
                    iterationImageData = []
                    iterationArticleData = []

                    navigationController?.pushViewController(uploadViewController, animated: true)
                }
                
            } else {
                alertController = UIAlertController(title: "Correct! Well Done!", message: "", preferredStyle: .alert)
                alertController.addAction(UIAlertAction(title: "OK", style: .default, handler: { action in
                    self.setupGame()
                }))
                self.present(alertController, animated: false)
            }
            
        } else {
            alertController = UIAlertController(title: "Wrong Answer! Please pay more attention next time!", message: "", preferredStyle: .alert)
            alertController.addAction(UIAlertAction(title: "OK", style: .default, handler: { action in
                self.setupGame()
            }))
            self.present(alertController, animated: false)
        }
   }
    
    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        let touch = touches.first!
        let location = touch.location(in: self.view)
        let force = touch.force
//        print(Date().timeIntervalSince1970 * 1000, location, force)
    }
    
    func showToast(controller: UIViewController, message : String, seconds: Double) {
        let alert = UIAlertController(title: nil, message: message, preferredStyle: .alert)
        alert.view.backgroundColor = UIColor.black
        //        alert.view.alpha = 0.2
        alert.view.layer.cornerRadius = 15

        controller.present(alert, animated: true)

        DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + seconds) {
            alert.dismiss(animated: true)
        }
    }
}

