PLANT_DATABASE = {
    'ミニトマト': {
        'base_temp': 10.0, 'image_url': 'https://images.pexels.com/photos/7208483/pexels-photo-7208483.jpeg', 'avg_gdd_per_day': 15,
        'events': [
            {
                'gdd': 300, 'advice': '最初の追肥のタイミングです！', 
                'what': '「野菜の肥料」と書かれた、栄養バランスの良いものがおすすめです。', 
                'how': '一株あたり約10g（大さじ1杯程度）を、株元から少し離して円を描くように与えます。', 
                'product_name': 'トマトの追肥用肥料', 'affiliate_link': 'https://amzn.to/40aoawy', 'recommendation_reason': 'この時期は実をつけ始める大切な時期。バランスの取れた栄養が、甘くて美味しいトマトを育てる秘訣です。'
            },
            {'gdd': 900, 'advice': '収穫まであと少し！', 'what': '水やり管理', 'how': '土の表面が乾いたら、朝のうちにたっぷりと与えましょう。実が赤くなり始めたら、少し乾燥気味にすると糖度が上がります。'}
        ]
    },
    'きゅうり': {
        'base_temp': 12.0, 'image_url': 'https://images.pexels.com/photos/7543157/pexels-photo-7543157.jpeg', 'avg_gdd_per_day': 20,
        'events': [
            {
                'gdd': 250, 'advice': '最初の追肥のタイミングです。', 
                'what': '化成肥料', 'how': '株元にパラパラと少量まき、土と軽く混ぜ合わせます。',
                'product_name': 'きゅうりの肥料', 'affiliate_link': 'https://amzn.to/3GoDfE7', 'recommendation_reason': 'きゅうりは生育が早い分、たくさんの栄養を必要とします。専用の肥料で元気に育てましょう。'
            },
            {'gdd': 500, 'advice': '収穫が始まりました！', 'what': 'こまめな収穫', 'how': '実がなり始めたら、2週間に1回ほどのペースで追肥を続けると、長く収穫を楽しめます。'}
        ]
    },
    'なす': {
        'base_temp': 12.0, 'image_url': 'https://images.unsplash.com/photo-1639428134238-b548770d4b77?q=80&w=987&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'avg_gdd_per_day': 18,
        'events': [
            {
                'gdd': 350, 'advice': '最初の追肥のタイミングです。', 
                'what': '化成肥料', 'how': '株の周りに円を描くように肥料を与えましょう。',
                # ★★★ なすのおすすめ情報を最初のイベントに移動 ★★★
                'product_name': 'なす用の肥料', 'affiliate_link': 'https://amzn.to/4l1WcLW', 'recommendation_reason': '「なすは水と肥料で育つ」と言われるほど栄養が必要です。実をつけ続けるためのスタミナを補給しましょう。'
            },
            {'gdd': 800, 'advice': '最初の実がなり始めました！', 'what': '継続的な追肥', 'how': 'ここからは肥料切れに注意し、2週間に1回のペースで追肥を続けるのがおすすめです。'}
        ]
    },
    'ピーマン': {
        'base_temp': 15.0, 'image_url': 'https://images.pexels.com/photos/4943441/pexels-photo-4943441.jpeg', 'avg_gdd_per_day': 16,
        'events': [
            {
                'gdd': 400, 'advice': '一番花が咲いたら追肥のサインです！', 
                'what': '化成肥料', 'how': '株元に少量与えます。',
                # ★★★ ピーマンのおすすめ情報を最初のイベントに移動 ★★★
                'product_name': 'ピーマン・パプリカの肥料', 'affiliate_link': 'https://amzn.to/4kl8ldT', 'recommendation_reason': '液体肥料は即効性があり、すぐに栄養を届けたいこの時期にぴったりです。'
            },
            {'gdd': 900, 'advice': '実がなり始めました。', 'what': '水やり管理', 'how': '乾燥に注意し、水やりを欠かさないようにしましょう。'}
        ]
    },
    'えだまめ': {
        'base_temp': 10.0, 'image_url': 'https://images.pexels.com/photos/2551790/pexels-photo-2551790.jpeg', 'avg_gdd_per_day': 18,
        'events': [
            {
                'gdd': 250, 'advice': '花が咲き始めたら、追肥のタイミングです。', 
                'what': 'リン酸・カリウムが多めの肥料', 'how': '窒素分が多いと葉ばかり茂るので注意。株元に軽く一握り与えましょう。',
                'product_name': '豆類専用の肥料', 'affiliate_link': 'https://amzn.to/3TfX1EP', 'recommendation_reason': 'えだまめは自分で窒素を作れるため、実や根の成長を助けるリン酸・カリウムが中心の肥料が効果的です。'
            },
            {'gdd': 600, 'advice': 'さやが膨らんできました！収穫が楽しみですね。', 'what': '水やり', 'how': '乾燥はさやの成長に影響します。特にこの時期は水を切らさないようにしましょう。'}
        ]
    },
    'しそ': {
        'base_temp': 15.0, 'image_url': 'https://images.pexels.com/photos/13532392/pexels-photo-13532392.jpeg', 'avg_gdd_per_day': 12,
        'events': [{'gdd': 150, 'advice': '本葉が10枚以上になったら、摘心（てきしん）をしましょう。', 'what': '一番上の芽', 'how': '先端をハサミでカットすると、脇芽が増えて収穫量がアップします。'}, {'gdd': 300, 'advice': '収穫が始まります！葉が茂ってきたら、2週間に1回程度の追肥を。', 'what': '液体肥料', 'how': '規定の倍率に薄めたものを、水やり代わりに与えると手軽です。'}]
    }
}
