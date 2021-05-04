//
//  ConsentData.swift
//  TouchCollect
//
//  Created by Henry on 28/01/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import Foundation
import UIKit

class ConsentData {
    var image: UIImage
    var title: String
    var ticked: Bool
    
    init(image: UIImage, title: String){
        self.image = image
        self.title = title
        self.ticked = false
    }
}
