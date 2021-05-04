//
//  ConsentCell.swift
//  TouchCollect
//
//  Created by Henry on 28/01/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import UIKit

class ConsentCell: UITableViewCell {

    @IBOutlet weak var consentText: UILabel!
    @IBOutlet weak var consentCheckbox: UIButton!
    
    func setConsent(consent: ConsentData) {
        consentText.text = consent.title
        consentCheckbox.setBackgroundImage(consent.image, for: .normal)
    }
    
    func flipImage() {
        if (consentCheckbox.backgroundImage(for: .normal) == UIImage(systemName: "square")){
            consentCheckbox.setBackgroundImage(UIImage(systemName: "checkmark.square"), for: .normal)
        } else {
            consentCheckbox.setBackgroundImage(UIImage(systemName: "square"), for: .normal)
        }
    }
}
