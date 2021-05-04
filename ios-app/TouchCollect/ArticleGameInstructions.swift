//
//  ArticleGameInstructions.swift
//  TouchCollect
//
//  Created by Henry on 30/01/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import UIKit

class ArticleGameInstructions: UIViewController {
    @IBOutlet weak var bStart: UIButton!

    var iterationArticleData: [[String: Any]] = []
    var iterationImageData: [[String: Any]] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        
        bStart.contentEdgeInsets = UIEdgeInsets(top: 10.0, left: 30.0, bottom: 10.0, right: 30.0)
        bStart.layer.cornerRadius = 20
        
        self.title = "Article Game Instructions"
        
        if (!iterationImageData.isEmpty){
            self.navigationItem.hidesBackButton = true
        }

        navigationController?.navigationBar.barStyle = .black
        navigationController?.navigationBar.tintColor = UIColor.white
        
        var alertController: UIAlertController
        alertController = UIAlertController(title: "Make sure you complete the tasks yourself (do not hand your phone to someone else to do so)", message: "", preferredStyle: .alert)
        alertController.addAction(UIAlertAction(title: "OK", style: .default))
        self.present(alertController, animated: false)
    }
    
    @IBAction func bContinue(_ sender: Any) {
        let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
        var nextViewController: ArticleGame

        nextViewController = storyBoard.instantiateViewController(withIdentifier: "ArticleGame") as! ArticleGame
        
        nextViewController.iterationArticleData = iterationArticleData
        nextViewController.iterationImageData = iterationImageData

        navigationController?.pushViewController(nextViewController, animated: true)
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
