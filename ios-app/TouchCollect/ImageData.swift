//
//  ArticleData.swift
//  TouchCollect
//
//  Created by Henry on 05/02/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import Foundation
import UIKit

struct ImageStruct: Hashable, Codable, Identifiable {
    var id: Int
    var question: String
    var designation: String
    var images: [String]
    var occurances: [Int]
}

class CImage {
    var imageName: String
    var designation: String
    var occurances: Int

    init(imageName: String, designation: String, occurances: Int){
        self.imageName = imageName
        self.designation = designation
        self.occurances = occurances
    }
}

let imageStruct: [ImageStruct] = load("imageData.json")
var allImages: [CImage] = generateImages()

func generateImages() -> [CImage] {
    var tmpCIM: [CImage] = []
    
    for imS in imageStruct {
        for i in 0 ..< imS.images.count{
            tmpCIM.append(CImage(imageName: imS.images[i], designation: imS.designation, occurances: imS.occurances[i]))
        }
    }
    
    return tmpCIM
}

