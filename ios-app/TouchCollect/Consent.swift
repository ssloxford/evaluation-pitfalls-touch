//
//  Consent.swift
//  TouchCollect
//
//  Created by Henry on 27/01/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import UIKit

class Consent: UITableViewController {
     
    var consentData: [ConsentData] = []
    var cells: [ConsentCell] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        consentData = createArray()
        navigationController?.navigationBar.barStyle = .black
    

        
        self.title = "Consent Form"
        self.navigationItem.hidesBackButton = true
    }

    override var preferredStatusBarStyle: UIStatusBarStyle {
        .lightContent
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        setNeedsStatusBarAppearanceUpdate()
    }

    
    func createArray() -> [ConsentData]{
        var tmp: [ConsentData] = []
        
        tmp.append(ConsentData(image: UIImage(systemName: "square")!, title: "1. I confirm that I have read and understand the information sheet for the above study.  I have had the opportunity to consider the information, ask questions and have had these answered satisfactorily."))
        tmp.append(ConsentData(image: UIImage(systemName: "square")!, title: "2. I understand that my participation is voluntary and that I am free to withdraw at any time, without giving any reason, and without any adverse consequences or academic penalty."))
        tmp.append(ConsentData(image: UIImage(systemName: "square")!, title: "3. I understand that research data collected during the study may be looked at by designated individuals from the University of Oxford where it is relevant to my taking part in this study. I give permission for these individuals to access my data."))
        tmp.append(ConsentData(image: UIImage(systemName: "square")!, title: "4. I understand that this project has been reviewed by, and received ethics clearance through, the University of Oxford Central University Research Ethics Committee."))
        tmp.append(ConsentData(image: UIImage(systemName: "square")!, title: "5. I understand who will have access to personal data provided, how the data will be stored and what will happen to the data at the end of the project."))
        tmp.append(ConsentData(image: UIImage(systemName: "square")!, title: "6. I understand how this research will be written up and published."))
        tmp.append(ConsentData(image: UIImage(systemName: "square")!, title: "7. I understand how to raise a concern or make a complaint."))
        tmp.append(ConsentData(image: UIImage(systemName: "square")!, title: "8. I consent to touchscreen sensor data being collected."))
        tmp.append(ConsentData(image: UIImage(systemName: "square")!, title: "9. I agree to take part in the study."))
        tmp.append(ConsentData(image: UIImage(systemName: "square")!, title: "10. I agree for research data collected in this study to be given to researchers, including those working outside of the EU, to be used in other research studies. I understand that any data that leave the research group will be fully anonymised so that I cannot be identified."))

        return tmp
    }
    
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return consentData.count + 1
    }
        
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
                
        if (indexPath.row != consentData.count){
            let consentRow = consentData[indexPath.row]
            
            if (cells.count < consentData.count ){
                cells.append(tableView.dequeueReusableCell(withIdentifier: "ConsentList", for: indexPath) as! ConsentCell)
            }
            let cell = cells[indexPath.row]
            cell.selectionStyle = .none

            cell.setConsent(consent: consentRow)
                    
            return cell;
        } else {
            let cell = tableView.dequeueReusableCell(withIdentifier: "ConsentContinue", for: indexPath) as! ConsentCellContinue
                        
            return cell;
        }
    }

    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        if (indexPath.row != consentData.count){
            if (!consentData[indexPath.row].ticked) {
                consentData[indexPath.row].image = UIImage(systemName: "checkmark.square")!
            } else {
                consentData[indexPath.row].image = UIImage(systemName: "square")!
            }
            
            cells[indexPath.row].flipImage()
            consentData[indexPath.row].ticked = !consentData[indexPath.row].ticked
        } else {
            var hasConsented = true
            
            for i in 0 ..< consentData.count {
                if (consentData[i].ticked == false) {
                    hasConsented = false
                    break
                }
            }
            
            if (hasConsented) {
                let storyBoard : UIStoryboard = UIStoryboard(name: "Main", bundle:nil)
                var nextViewController: UIViewController

                nextViewController = storyBoard.instantiateViewController(withIdentifier: "Details") as! Details

                navigationController?.pushViewController(nextViewController, animated: true)
            } else {
                showToast(controller: self, message : "Please consent to all compulsary statements", seconds: 2.0)
            }
        }
    }
    
 func showToast(controller: UIViewController, message : String, seconds: Double) {
        let alert = UIAlertController(title: nil, message: message, preferredStyle: .alert)
        alert.view.backgroundColor = UIColor.black
        alert.view.alpha = 0.5
        alert.view.layer.cornerRadius = 15

        controller.present(alert, animated: true)

        DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + seconds) {
            alert.dismiss(animated: true)
        }
    }
}

