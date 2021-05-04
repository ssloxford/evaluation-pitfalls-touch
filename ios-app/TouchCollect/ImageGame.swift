//
//  ImageGame.swift
//  TouchCollect
//
//  Created by Henry on 27/01/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import UIKit
import CoreMotion
import UIKit.UIGestureRecognizerSubclass


class ATScrollView: UIScrollView, UIGestureRecognizerDelegate {
    func gestureRecognizer(_ gestureRecognizer: UIGestureRecognizer,
                           shouldRecognizeSimultaneouslyWith otherGestureRecognizer: UIGestureRecognizer) -> Bool {
        return true
    }
}

class ImmediatePanG: UIPanGestureRecognizer {
       var force = CGFloat(0)
       var area = CGFloat(0)
       
       override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent) {
        force = touches.first!.force
        area = touches.first!.majorRadius
        super.touchesBegan(touches, with: event)
        self.state = .began

       }
       
       override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent) {
            force = touches.first!.force
            area = touches.first!.majorRadius
            super.touchesMoved(touches, with: event)
       }
       
       override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent) {
         force = touches.first!.force
         area = touches.first!.majorRadius

         super.touchesEnded(touches, with: event)
         self.state = .ended
       }
}

class ImageGame: UIViewController, UIScrollViewDelegate {
    
    @IBOutlet weak var iArrow: UIImageView!
    @IBOutlet weak var mainScrollView: UIScrollView!
    @IBAction func handlePan(_ recognizer: ImmediatePanG) {
        
        if (!iArrow.isHidden) {
            iArrow.isHidden = true;
        }
        
        let location = recognizer.location(in: view)
        let time = Date().timeIntervalSince1970 * 1000
        
        switch recognizer.state {
        case .began:
            print("STARTED")
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
            print(time,Double(location.x),Double(location.y),Double(recognizer.force),Double(recognizer.area))
            print("ENDED")
            break
        default:
            break
        }
    }
    
    
    var imageArray = [UIImage]()
    var motion = CMMotionManager()
    var answer = 0
    var question = ""
    var correct = 0
    let goal = 5
    let minImages = 2
    let maxImages = 6
    let totalImages = 20
    var iterationCount = 0
    
    var iterationArticleData: [[String: Any]] = []
    var iterationImageData: [[String: Any]] = []
    
    var gyroscopeData: [[String: Any]] = []
    var accelData: [[String: Any]] = []
    var touchData: [[String: Any]] = []
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.navigationItem.hidesBackButton = true
        
        
        mainScrollView.delegate = self
        mainScrollView.frame = view.frame
        
        setupGame()
        setupSensors()
                
        UIView.animate(withDuration: 1, delay: 0, options: [.repeat, .autoreverse], animations: {
            self.iArrow.transform = CGAffineTransform(translationX: -100, y: 0)
        })
    }
    
    func setupGame(){
        let designationId = Int.random(in: 0 ..< (imageStruct.count))
        if let navigationBar = self.navigationController?.navigationBar {
            for view in navigationBar.subviews {
                view.removeFromSuperview()
            }
            
            let firstFrame = CGRect(x: 10, y: 0, width: navigationBar.frame.width-80, height: navigationBar.frame.height)
            let secondFrame = CGRect(x: navigationBar.frame.width-60, y: 0, width: 60, height: navigationBar.frame.height)

            let firstLabel = UILabel(frame: firstFrame)
            firstLabel.text = imageStruct[designationId].question
            firstLabel.numberOfLines = 2
            firstLabel.font = UIFont.boldSystemFont(ofSize: 17.0)
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
        
        answer = 0
        question = imageStruct[designationId].question
        imageArray = generateImageArray(designationId: designationId)
        
        for view in mainScrollView.subviews {
            view.removeFromSuperview()
        }
        
        for i in 0..<imageArray.count{
            let imageView = UIImageView()
            imageView.image = imageArray[i]
            imageView.contentMode = .scaleAspectFit
            let xPos = self.view.frame.width * CGFloat(i)
            imageView.frame = CGRect(x: xPos, y: -50, width: self.mainScrollView.frame.width, height: self.mainScrollView.frame.height)
            imageView.isUserInteractionEnabled = true
            
            mainScrollView.contentSize.width = mainScrollView.frame.width * CGFloat(i + 1)
            mainScrollView.addSubview(imageView)
        }
        
        print(answer)
    }
    
    func generateImageArray(designationId: Int) -> [UIImage] {
        var imageNames: [String] = []
        var images: [UIImage] = []
        answer = 0
        
        let nImages = Int.random(in: minImages ..< maxImages+1)
        let designation = imageStruct[designationId].designation
        var tmpImages: [CImage] = []
        
        for im in allImages {
            if (im.designation == designation){
                tmpImages.append(im)
            }
        }
        
        tmpImages.shuffle()
        tmpImages = Array(tmpImages.prefix(nImages))
        
        for im in tmpImages {
            imageNames.append(im.imageName)
            answer += im.occurances
        }
        
        var i = imageNames.count
         
        while (i < totalImages) {
            let entry = Int.random(in: 0 ..< allImages.count)
            
            if (!imageNames.contains(allImages[entry].imageName) && allImages[entry].designation != imageStruct[designationId].designation){
                imageNames.append(allImages[entry].imageName)
                i += 1
            }
        }
        
        imageNames.shuffle()
        imageNames.append("dissapear")
        
        for imName in imageNames {
            images.append(UIImage(named: imName)!)
        }
        
        return images
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
    
    
    func scrollViewDidEndDecelerating(_ scrollView: UIScrollView) {

        let pageNumber = round(scrollView.contentOffset.x / scrollView.frame.size.width)
        if pageNumber == CGFloat(totalImages) {
            let tempQ = String(question.dropFirst(10).dropLast(24)).capitalizingFirstLetter()
            let alert = UIAlertController(title: tempQ, message: "", preferredStyle: .alert)
            alert.addTextField { (textField) in
                textField.text = ""
                textField.keyboardType = .numberPad
            }

            alert.addAction(UIAlertAction(title: "Submit", style: .default, handler: { [weak alert] (_) in
                let textField = alert!.textFields![0] // Force unwrapping because we know it exists.
                var alertController: UIAlertController
                
//                self.accelData.append(
//                    [
//                        "timestamp": Date().timeIntervalSince1970 * 1000,
//                        "x": 1,
//                        "y": 2,
//                        "z": 3
//                    ]
//                )
//
//                self.gyroscopeData.append(
//                    [
//                        "timestamp": Date().timeIntervalSince1970 * 1000,
//                        "x": 1,
//                        "y": 2,
//                        "z": 3
//                    ]
//                )
            
                self.iterationImageData.append([
                    "id": self.iterationCount,
                    "touch": self.touchData,
                    "accel": self.accelData,
                    "gyro": self.gyroscopeData
                ])
            
                self.touchData = []
                self.accelData = []
                self.gyroscopeData = []

                self.iterationCount += 1
                
                if (String(self.answer) == textField.text){
                    self.correct += 1
                    
                    if (self.correct == self.goal) {
                        for view in (self.navigationController?.navigationBar.subviews)! {
                             view.removeFromSuperview()
                        }
                        
                            let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
                            
                            if (self.iterationArticleData.isEmpty) {
                                var articleViewController: ArticleGameInstructions

                                articleViewController = storyBoard.instantiateViewController(withIdentifier: "ArticleGameInstructions") as! ArticleGameInstructions
                                articleViewController.iterationImageData = self.iterationImageData
                                
                                self.iterationImageData = []
                                self.iterationArticleData = []

                                self.navigationController?.pushViewController(articleViewController, animated: true)
                            } else {
                                var uploadViewController: Upload

                                uploadViewController = storyBoard.instantiateViewController(withIdentifier: "Upload") as! Upload

                                uploadViewController.iterationImageData = self.iterationImageData
                                uploadViewController.iterationArticleData = self.iterationArticleData
                                
                                self.iterationImageData = []
                                self.iterationArticleData = []

                                self.navigationController?.pushViewController(uploadViewController, animated: true)
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
                
            }))

            // 4. Present the alert.
            self.present(alert, animated: false)
        }
        
        
    }
}

extension String {
    func capitalizingFirstLetter() -> String {
      return prefix(1).uppercased() + self.lowercased().dropFirst()
    }

    mutating func capitalizeFirstLetter() {
      self = self.capitalizingFirstLetter()
    }
}

@IBDesignable class PaddingLabelBar: UILabel {

    @IBInspectable var topInset: CGFloat = 20.0
    @IBInspectable var bottomInset: CGFloat = 20.0
    @IBInspectable var leftInset: CGFloat = 0.0
    @IBInspectable var rightInset: CGFloat = 0.0

    override func drawText(in rect: CGRect) {
        let insets = UIEdgeInsets(top: topInset, left: leftInset, bottom: bottomInset, right: rightInset)
        super.drawText(in: rect.inset(by: insets))
    }

    override var intrinsicContentSize: CGSize {
        let size = super.intrinsicContentSize
        return CGSize(width: size.width + leftInset + rightInset,
                      height: size.height + topInset + bottomInset)
    }
}
