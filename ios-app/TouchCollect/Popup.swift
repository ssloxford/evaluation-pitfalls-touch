//
//  Popup.swift
//  TouchCollect
//
//  Created by Henry on 05/03/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import UIKit

class Popup: UIViewController {
    @IBOutlet weak var bOkay: UIButton!
    @IBOutlet weak var insideVIew: UIView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        insideVIew.layer.cornerRadius = 20
        self.view.backgroundColor = UIColor.black.withAlphaComponent(0.8)
        
        self.showAnimate()

    }
    
    @IBAction func closePopup(_ sender: Any) {
        self.removeAnimate()
    }
    
    func showAnimate(){
        self.view.transform = CGAffineTransform(scaleX: 1.3, y: 1.3)
        self.view.alpha = 0.0;
        UIView.animate(withDuration: 0.25, animations: {
            self.view.alpha = 1.0
            self.view.transform = CGAffineTransform(scaleX: 1.0, y: 1.0)
        });
    }
    
    func removeAnimate(){
        UIView.animate(withDuration: 0.25, animations: {
            self.view.transform = CGAffineTransform(scaleX: 1.3, y: 1.3)
            self.view.alpha = 0.0;
        }, completion: {(finished: Bool) in
            if (finished){
                self.view.removeFromSuperview()
            }
        });
    }
    
    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}
