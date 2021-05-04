//
//  Final.swift
//  TouchCollect
//
//  Created by Henry on 13/02/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import UIKit

class Final: UIViewController {
    @IBOutlet weak var lCode: UILabel!
    @IBOutlet weak var bHome: UIButton!
        
    override func viewDidLoad() {
        super.viewDidLoad()
        
        navigationController?.navigationBar.barStyle = .black

        self.title = "Mechanical Turk Code"
        self.navigationController?.setNavigationBarHidden(true, animated:false)
        self.navigationItem.hidesBackButton = true

        bHome.contentEdgeInsets = UIEdgeInsets(top: 10.0, left: 30.0, bottom: 10.0, right: 30.0)
        bHome.layer.cornerRadius = 20
        
        let defaults = UserDefaults.standard
        defaults.set(false, forKey: "is_first")
        
        lCode.text = defaults.string(forKey: "mturk_token")
    }    

    @IBAction func goHome(_ sender: Any) {
        let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
        var nextViewController: Start
        
        nextViewController = storyBoard.instantiateViewController(withIdentifier: "Start") as! Start

        navigationController?.pushViewController(nextViewController, animated: true)
    }
}
