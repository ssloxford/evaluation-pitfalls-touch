//
//  StartViewController.swift
//  TouchCollect
//
//  Created by Henry on 27/01/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import UIKit
import Alamofire

class Start: UIViewController {
    
    @IBOutlet weak var buttonEnrollOrStart: UIButton!
    @IBOutlet weak var bGame1: UIButton!
    @IBOutlet weak var lStreak: UILabel!
    @IBOutlet weak var bTurk: UIButton!
    @IBOutlet weak var lnStreak: UILabel!
    @IBOutlet weak var lEarned: UILabel!
    @IBOutlet weak var lNext: UILabel!
    @IBOutlet weak var lPotential: UILabel!
    @IBOutlet weak var lTimeArticle: UILabel!
    @IBOutlet weak var iFlame: UIImageView!
    
    var showPopup = false
    var showMoney = false
    var activityIndicator: UIActivityIndicatorView = UIActivityIndicatorView()
    
    override func viewDidLoad() {
        super.viewDidLoad()

        let notificationCenter = NotificationCenter.default
        notificationCenter.addObserver(self, selector: #selector(appMovedToForeground), name: UIApplication.willEnterForegroundNotification, object: nil)
    }

    @objc func appMovedToForeground() {
        loadMainScreen();
    }
    
    override func viewDidAppear(_ animated: Bool) {
        loadMainScreen();
    }
    
    func loadMainScreen() {
        if self.traitCollection.forceTouchCapability == .available {
                navigationController?.navigationBar.barStyle = .default
                
                navigationController?.navigationBar.barTintColor = UIColor( red: CGFloat(244/255.0), green: CGFloat(112/255.0), blue: CGFloat(91/255.0), alpha: CGFloat(1.0) )
                navigationController?.navigationBar.titleTextAttributes = [.foregroundColor: UIColor.white]
                tabBarController?.tabBar.barTintColor = UIColor.brown
                tabBarController?.tabBar.tintColor = UIColor.yellow
                
                if (showPopup) {
                    let popup = UIStoryboard(name: "Main", bundle: nil).instantiateViewController(withIdentifier: "Popup") as! Popup
                    
                    self.addChild(popup)
                    popup.view.frame = self.view.frame
                    self.view.addSubview(popup.view)
                    popup.didMove(toParent: self)
                }
                
                if Reachability.isConnectedToNetwork(){
                
                    let defaults = UserDefaults.standard
                    if (defaults.bool(forKey: "enrolled")) {
                        activityIndicator.center = self.view.center
                        activityIndicator.hidesWhenStopped = true
                        activityIndicator.style = .large
                        
                        view.addSubview(activityIndicator)
                        
                        activityIndicator.startAnimating()

                        
                         let parameters: Parameters = [
                                   "uuid": defaults.string(forKey: "uuid"),
                               ]
                        
                        AF.request("https://ssloxford.co.uk:8009/query_state", method: .post, parameters: parameters, encoding: JSONEncoding.default).validate(statusCode: 200..<300).responseJSON { response in
                            print(response)
                            switch(response.result) {
                            case .success(let JSON):
                                let resp = JSON as! NSDictionary
                                let streak = resp.object(forKey: "streak_current")! as! Int
                                let cents = resp.object(forKey: "total_so_far")! as! Int
                                let blacklisted = resp.object(forKey: "blacklisted")! as! Int
                                let next_cents = resp.object(forKey: "value_of_next")! as! Int
                                let earning_potential = resp.object(forKey: "remaining_earning_potential")! as! Int
                                let can_submit = resp.object(forKey: "can_submit")! as! Int
                                let study_active = resp.object(forKey: "study_active")! as! Int
                                let current_build = resp.object(forKey: "build_version")! as! String
                                                        
                                if (Bundle.main.buildVersionNumber != current_build){
                                    var alertController: UIAlertController
                                    alertController = UIAlertController(title: "Please update the app to the newest version from the TestFlight app!", message: "", preferredStyle: .alert)
                                    self.present(alertController, animated: false)
                                }
                                
                                if (blacklisted != 0){
                                    let blacklisted_msg = resp.object(forKey: "blacklisted_msg")! as! String
                                    var alertController: UIAlertController
                                    alertController = UIAlertController(title: blacklisted_msg, message: "", preferredStyle: .alert)
                                    self.present(alertController, animated: false)
                                }
                                
                                if (study_active == 0){
                                    var alertController: UIAlertController
                                    alertController = UIAlertController(title: "Thank you for taking part of our experiment!", message: "", preferredStyle: .alert)
                                    self.present(alertController, animated: false)
                                }
                                
                                
                                self.activityIndicator.stopAnimating()
                                self.bGame1.contentEdgeInsets = UIEdgeInsets(top: 20.0, left: 40.0, bottom: 20.0, right: 40.0)
                                self.bGame1.layer.cornerRadius = 20

                                self.bGame1.isHidden = false
                                self.lStreak.isHidden = false
                                self.lnStreak.isHidden = false
                                self.lnStreak.text = String(streak)
                                
                                self.lEarned.isHidden = false
                                self.lEarned.text = "Earned: " + String(format: "%.2f", Float(0)/100) + "$"

                                
                                self.lNext.isHidden = false
                                self.lNext.text = "Next payment: " + String(format: "%.2f", Float(next_cents)/100) + "$"
                                    
                                self.lPotential.isHidden = false
                                self.lPotential.text = "You can still earn:  " + String(format: "%.2f", Float(earning_potential)/100) + "$"

                                self.iFlame.isHidden = false

                                if (can_submit != 1) {
                                    self.bGame1.backgroundColor = UIColor.tertiaryLabel
                                    self.bGame1.isEnabled = false
                                    self.lTimeArticle.text = "Come back tomorrow"
                                    self.lTimeArticle.isHidden = false
                                }
                                
                                
                                if (defaults.bool(forKey: "shown_turk")) {
                                    self.bTurk.isHidden = false
                                    self.lEarned.text = "Earned: " + String(format: "%.2f", Float(cents)/100) + "$"
                                    
                                    
                                    self.iFlame.isUserInteractionEnabled = true
                                    let longPressRecognizer = UILongPressGestureRecognizer(target: self, action: #selector(self.longPressed))
                                    longPressRecognizer.minimumPressDuration = 2
                                    self.iFlame.addGestureRecognizer(longPressRecognizer)

                                }
                                
                                if (self.showMoney){
                                    var alertController: UIAlertController
                                    alertController = UIAlertController(title: "You will automatically receive your bonus payment for completing this task. A confirmation email from Amazon Mechanical Turk will be sent to you.", message: "", preferredStyle: .alert)
                                    alertController.addAction(UIAlertAction(title: "OK", style: .default))
                                    self.present(alertController, animated: false)
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
                    } else {
                        self.view.backgroundColor = UIColor(patternImage: UIImage(named: "background.png")!)
                        buttonEnrollOrStart.contentEdgeInsets = UIEdgeInsets(top: 15.0, left: 30.0, bottom: 15.0, right: 30.0)
                        buttonEnrollOrStart.layer.cornerRadius = 20
                        buttonEnrollOrStart.isHidden = false
                    }
                } else {
                    var alertController: UIAlertController
                    alertController = UIAlertController(title: "Cannot connect to the internet", message: "Please enable internet connection and start the app again", preferredStyle: .alert)
                    alertController.addAction(UIAlertAction(title: "OK", style: .default, handler: { action in
                        exit(0)
                    }))
                    self.present(alertController, animated: false)
                }
                
                self.title = "Welcome"
                    
                } else {
                    var alertController: UIAlertController
                    let models = ["iPhone 6s", "iPhone 6s Plus", "iPhone 7", "iPhone 7 Plus", "iPhone 8", "iPhone 8 Plus", "iPhone X", "iPhone XS", "iPhone XS Max"]

                    if (models.contains(String(UIDevice.modelName))){
                        alertController = UIAlertController(title: "Please enable 3D touch from Settings > General > Accessibility > 3D Touch", message: "", preferredStyle: .alert)
                    } else {
                        alertController = UIAlertController(title: "This device is not supported by our experiment. The supported devices are: iPhone 6S, 6S Plus, 7, 7 Plus, 8, 8 Plus, X, XS and XS Max", message: "", preferredStyle: .alert)
                    }
                    self.present(alertController, animated: false)
                }
    }
    
    @objc func longPressed() {
        UIPasteboard.general.string = UserDefaults.standard.string(forKey: "uuid")
        var alertController: UIAlertController
        alertController = UIAlertController(title: "UUID copied to clipboard", message: "", preferredStyle: .alert)
        alertController.addAction(UIAlertAction(title: "OK", style: .default))
        self.present(alertController, animated: false)
    }
    
    @IBAction func enrollOrStart(_ sender: Any) {
        let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
        var nextViewController: UIViewController

        nextViewController = storyBoard.instantiateViewController(withIdentifier: "Consent") as! Consent

        navigationController?.pushViewController(nextViewController, animated: true)
    }
    
    @IBAction func startArticleGame(_ sender: Any) {
        
        let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
        let isArticleFirst = Bool.random()
        var nextViewController: UIViewController

        if (isArticleFirst) {
            nextViewController = storyBoard.instantiateViewController(withIdentifier: "ArticleGameInstructions") as! ArticleGameInstructions

        } else {
            nextViewController = storyBoard.instantiateViewController(withIdentifier: "ImageGameInstructions") as! ImageGameInstructions
        }
        
        navigationController?.pushViewController(nextViewController, animated: true)
    }
    
    
    @IBAction func openTurk(_ sender: Any) {
        let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
        var nextViewController: UIViewController
        
        nextViewController = storyBoard.instantiateViewController(withIdentifier: "Final") as! Final

        navigationController?.pushViewController(nextViewController, animated: true)
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        navigationController?.setNavigationBarHidden(true, animated: animated)
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        navigationController?.setNavigationBarHidden(false, animated: animated)
    }
    
}


public extension UIDevice {
    
    static let modelName: String = {
        var systemInfo = utsname()
        uname(&systemInfo)
        let machineMirror = Mirror(reflecting: systemInfo.machine)
        let identifier = machineMirror.children.reduce("") { identifier, element in
            guard let value = element.value as? Int8, value != 0 else { return identifier }
            return identifier + String(UnicodeScalar(UInt8(value)))
        }
        
        func mapToDevice(identifier: String) -> String { // swiftlint:disable:this cyclomatic_complexity
            #if os(iOS)
            switch identifier {
            case "iPod5,1":                                 return "iPod Touch 5"
            case "iPod7,1":                                 return "iPod Touch 6"
            case "iPhone3,1", "iPhone3,2", "iPhone3,3":     return "iPhone 4"
            case "iPhone4,1":                               return "iPhone 4s"
            case "iPhone5,1", "iPhone5,2":                  return "iPhone 5"
            case "iPhone5,3", "iPhone5,4":                  return "iPhone 5c"
            case "iPhone6,1", "iPhone6,2":                  return "iPhone 5s"
            case "iPhone7,2":                               return "iPhone 6"
            case "iPhone7,1":                               return "iPhone 6 Plus"
            case "iPhone8,1":                               return "iPhone 6s"
            case "iPhone8,2":                               return "iPhone 6s Plus"
            case "iPhone9,1", "iPhone9,3":                  return "iPhone 7"
            case "iPhone9,2", "iPhone9,4":                  return "iPhone 7 Plus"
            case "iPhone8,4":                               return "iPhone SE"
            case "iPhone10,1", "iPhone10,4":                return "iPhone 8"
            case "iPhone10,2", "iPhone10,5":                return "iPhone 8 Plus"
            case "iPhone10,3", "iPhone10,6":                return "iPhone X"
            case "iPhone11,2":                              return "iPhone XS"
            case "iPhone11,4", "iPhone11,6":                return "iPhone XS Max"
            case "iPhone11,8":                              return "iPhone XR"
            case "iPad2,1", "iPad2,2", "iPad2,3", "iPad2,4":return "iPad 2"
            case "iPad3,1", "iPad3,2", "iPad3,3":           return "iPad 3"
            case "iPad3,4", "iPad3,5", "iPad3,6":           return "iPad 4"
            case "iPad4,1", "iPad4,2", "iPad4,3":           return "iPad Air"
            case "iPad5,3", "iPad5,4":                      return "iPad Air 2"
            case "iPad6,11", "iPad6,12":                    return "iPad 5"
            case "iPad7,5", "iPad7,6":                      return "iPad 6"
            case "iPad11,4", "iPad11,5":                    return "iPad Air (3rd generation)"
            case "iPad2,5", "iPad2,6", "iPad2,7":           return "iPad Mini"
            case "iPad4,4", "iPad4,5", "iPad4,6":           return "iPad Mini 2"
            case "iPad4,7", "iPad4,8", "iPad4,9":           return "iPad Mini 3"
            case "iPad5,1", "iPad5,2":                      return "iPad Mini 4"
            case "iPad11,1", "iPad11,2":                    return "iPad Mini 5"
            case "iPad6,3", "iPad6,4":                      return "iPad Pro (9.7-inch)"
            case "iPad6,7", "iPad6,8":                      return "iPad Pro (12.9-inch)"
            case "iPad7,1", "iPad7,2":                      return "iPad Pro (12.9-inch) (2nd generation)"
            case "iPad7,3", "iPad7,4":                      return "iPad Pro (10.5-inch)"
            case "iPad8,1", "iPad8,2", "iPad8,3", "iPad8,4":return "iPad Pro (11-inch)"
            case "iPad8,5", "iPad8,6", "iPad8,7", "iPad8,8":return "iPad Pro (12.9-inch) (3rd generation)"
            case "AppleTV5,3":                              return "Apple TV"
            case "AppleTV6,2":                              return "Apple TV 4K"
            case "AudioAccessory1,1":                       return "HomePod"
            case "i386", "x86_64":                          return "Simulator \(mapToDevice(identifier: ProcessInfo().environment["SIMULATOR_MODEL_IDENTIFIER"] ?? "iOS"))"
            default:                                        return identifier
            }
            #elseif os(tvOS)
            switch identifier {
            case "AppleTV5,3": return "Apple TV 4"
            case "AppleTV6,2": return "Apple TV 4K"
            case "i386", "x86_64": return "Simulator \(mapToDevice(identifier: ProcessInfo().environment["SIMULATOR_MODEL_IDENTIFIER"] ?? "tvOS"))"
            default: return identifier
            }
            #endif
        }
        
        return mapToDevice(identifier: identifier)
    }()
}


extension UINavigationController {
    func replaceCurrentViewControllerWith(viewController: UIViewController, animated: Bool) {
        var controllers = viewControllers
        controllers.removeLast()
        controllers.append(viewController)
        setViewControllers(controllers, animated: animated)
    }
}

extension Bundle {
    var releaseVersionNumber: String? {
        return infoDictionary?["CFBundleShortVersionString"] as? String
    }
    var buildVersionNumber: String? {
        return infoDictionary?["CFBundleVersion"] as? String
    }
}

extension UIImage {
    struct RotationOptions: OptionSet {
        let rawValue: Int

        static let flipOnVerticalAxis = RotationOptions(rawValue: 1)
        static let flipOnHorizontalAxis = RotationOptions(rawValue: 2)
    }

    func rotated(by rotationAngle: Measurement<UnitAngle>, options: RotationOptions = []) -> UIImage? {
        guard let cgImage = self.cgImage else { return nil }

        let rotationInRadians = CGFloat(rotationAngle.converted(to: .radians).value)
        let transform = CGAffineTransform(rotationAngle: rotationInRadians)
        var rect = CGRect(origin: .zero, size: self.size).applying(transform)
        rect.origin = .zero

        let renderer = UIGraphicsImageRenderer(size: rect.size)
        return renderer.image { renderContext in
            renderContext.cgContext.translateBy(x: rect.midX, y: rect.midY)
            renderContext.cgContext.rotate(by: rotationInRadians)

            let x = options.contains(.flipOnVerticalAxis) ? -1.0 : 1.0
            let y = options.contains(.flipOnHorizontalAxis) ? 1.0 : -1.0
            renderContext.cgContext.scaleBy(x: CGFloat(x), y: CGFloat(y))

            let drawRect = CGRect(origin: CGPoint(x: -self.size.width/2, y: -self.size.height/2), size: self.size)
            renderContext.cgContext.draw(cgImage, in: drawRect)
        }
    }
}
