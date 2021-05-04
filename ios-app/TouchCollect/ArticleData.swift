//
//  ArticleData.swift
//  TouchCollect
//
//  Created by Henry on 05/02/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import Foundation
import UIKit


class ArticleData {
    var id: Int
    var iUser: UIImage
    var iPost: UIImage
    var title: String
    var username: String
    var post: String
    var isImagePost: Bool
    var timePassed: String
    var comments: String
    var likes: String
    var question: String
    
    init(id: Int, iUser: UIImage, iPost: UIImage, title: String, username: String, post: String, isImagePost: Bool, timePassed: String, comments: String, likes: String, question: String){
        self.iUser = iUser
        self.iPost = iPost
        self.title = title.lowercased()
        self.username = username
        self.post = post
        self.isImagePost = isImagePost
        self.timePassed = timePassed
        self.comments = comments
        self.likes = likes
        self.question = question
        self.id = id
        
        self.title.capitalizeFirstLetter()
    }
}


struct ArticleStruct: Hashable, Codable, Identifiable {
    var id: Int
    var iPost: String
    var title: String
    var post: String
    var question: String
    var isImagePost: Bool
}


let articleStruct: [ArticleStruct] = load("articleData.json")

func load<T: Decodable>(_ filename: String) -> T {
    let data: Data
    
    guard let file = Bundle.main.url(forResource: filename, withExtension: nil)
        else {
            fatalError("Couldn't find \(filename) in main bundle.")
    }
    
    do {
        data = try Data(contentsOf: file)
    } catch {
        fatalError("Couldn't load \(filename) from main bundle:\n\(error)")
    }
    
    do {
        let decoder = JSONDecoder()
        return try decoder.decode(T.self, from: data)
    } catch {
        fatalError("Couldn't parse \(filename) as \(T.self):\n\(error)")
    }
}
