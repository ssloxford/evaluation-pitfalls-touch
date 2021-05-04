//
//  ConsentCell.swift
//  TouchCollect
//
//  Created by Henry on 28/01/2020.
//  Copyright © 2020 Martin. All rights reserved.
//

import UIKit

class ArticleGameCell: UITableViewCell {
    @IBOutlet weak var lName: UILabel!
    @IBOutlet weak var iUser: UIImageView!
    @IBOutlet weak var iArticle: UIImageView!
    @IBOutlet weak var lTitle: UILabel!
    @IBOutlet weak var lPost: UILabel!
    @IBOutlet weak var lTime: UILabel!
    @IBOutlet weak var lLikes: UILabel!
    @IBOutlet weak var lComments: UILabel!
    
    internal var aspectConstraint : NSLayoutConstraint? {
        didSet {
            if oldValue != nil {
                iArticle.removeConstraint(oldValue!)
            }
            if aspectConstraint != nil {
                iArticle.addConstraint(aspectConstraint!)
            }
        }
    }
    
    override func prepareForReuse() {
        super.prepareForReuse()
        aspectConstraint = nil
    }


    func setArticle(article: ArticleData) {
        lName.text = article.username
        iUser.image = article.iUser
        lPost.text = article.post
        lLikes.text = article.likes
        lComments.text = article.comments
        lTime.text = article.timePassed
        
        
        if (!article.isImagePost) {
            article.title = ""
            lTitle.backgroundColor = .systemBackground
            article.iPost = UIImage(named: "dissapear")!
        } else {
            lTitle.backgroundColor = .tertiarySystemFill
        }
        
        let aspect = article.iPost.size.width / article.iPost.size.height

        aspectConstraint = NSLayoutConstraint(item: iArticle!, attribute: NSLayoutConstraint.Attribute.width, relatedBy: NSLayoutConstraint.Relation.equal, toItem: iArticle!, attribute: NSLayoutConstraint.Attribute.height, multiplier: aspect, constant: 0.0)

        lTitle.text = article.title
        iArticle.image = article.iPost
        
    }
}


@IBDesignable class PaddingLabel: UILabel {

    @IBInspectable var topInset: CGFloat = 5.0
    @IBInspectable var bottomInset: CGFloat = 5.0
    @IBInspectable var leftInset: CGFloat = 10.0
    @IBInspectable var rightInset: CGFloat = 10.0

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
