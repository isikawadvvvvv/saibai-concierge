# plant_data.py
PLANT_DATABASE = {
    'ミニトマト': {
        'base_temp': 10.0, 'image_url': 'https://images.pexels.com/photos/7208483/pexels-photo-7208483.jpeg', 'avg_gdd_per_day': 15,
        'initial_products': [
            {'name': 'スターターセット', 'link': 'https://amzn.to/3yTqW4S', 'reason': '土、プランター、肥料が全部入りで初心者に最適！'},
            {'name': 'トマト用培養土', 'link': 'https://amzn.to/3VzXy8K', 'reason': '甘いトマトを育てるための栄養がたっぷり。'},
        ],
        'events': [
            {'gdd': 300, 'advice': '最初の追肥のタイミングです！', 'what': '「野菜の肥料」と書かれた、栄養バランスの良いものがおすすめです。', 'how': '一株あたり約10g（大さじ1杯程度）を、株元から少し離して円を描くように与えます。', 'product_name': 'トマトの追肥用肥料', 'affiliate_link': 'https://amzn.to/40aoawy', 'recommendation_reason': '実をつけ始める大切な時期。バランスの取れた栄養が、甘くて美味しいトマトを育てる秘訣です。'},
            {'gdd': 900, 'advice': '収穫まであと少し！', 'what': '水やり管理', 'how': '土の表面が乾いたら、朝のうちにたっぷりと与えましょう。実が赤くなり始めたら、少し乾燥気味にすると糖度が上がります。'}
        ]
    },
    'きゅうり': {
        'base_temp': 12.0, 'image_url': 'https://images.pexels.com/photos/7543157/pexels-photo-7543157.jpeg', 'avg_gdd_per_day': 20,
        'initial_products': [
            {'name': '緑のカーテンセット', 'link': 'https://amzn.to/3yWp9Jt', 'reason': 'きゅうりを育てるのに必要な支柱やネットが揃っています。'},
        ],
        'events': [
            {'gdd': 250, 'advice': '最初の追肥のタイミングです。', 'what': '化成肥料', 'how': '株元にパラパラと少量まき、土と軽く混ぜ合わせます。', 'product_name': 'きゅうりの肥料', 'affiliate_link': 'https://amzn.to/3GoDfE7', 'recommendation_reason': '生育が早い分、たくさんの栄養を必要とします。専用の肥料で元気に育てましょう。'}
        ]
    },
    'なす': {
        'base_temp': 12.0, 'image_url': 'https://images.unsplash.com/photo-1639428134238-b548770d4b77?q=80&w=987&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'avg_gdd_per_day': 18,
        'initial_products': [
            {'name': 'なす用肥料', 'link': 'https://amzn.to/4l1WcLW', 'reason': '「なすは水と肥料で育つ」と言われるほど栄養が必要です。'},
        ],
        'events': [
            {'gdd': 350, 'advice': '最初の追肥のタイミングです。', 'what': '化成肥料', 'how': '株の周りに円を描くように肥料を与えましょう。', 'product_name': 'なす用の肥料', 'affiliate_link': 'https://amzn.to/4l1WcLW', 'recommendation_reason': '「なすは水と肥料で育つ」と言われるほど栄養が必要です。実をつけ続けるためのスタミナを補給しましょう。'},
            {'gdd': 800, 'advice': '最初の実がなり始めました！', 'what': '継続的な追肥', 'how': 'ここからは肥料切れに注意し、2週間に1回のペースで追肥を続けるのがおすすめです。'}
        ]
    },
    'ピーマン': {
        'base_temp': 15.0, 'image_url': 'https://images.pexels.com/photos/4943441/pexels-photo-4943441.jpeg', 'avg_gdd_per_day': 16,
        'initial_products': [
            {'name': 'ピーマン・パプリカの肥料', 'link': 'https://amzn.to/4kl8ldT', 'reason': '甘くて美味しいピーマンを育てるための専用肥料です。'},
        ],
        'events': [
            {'gdd': 400, 'advice': '一番花が咲いたら追肥のサインです！', 'what': '化成肥料', 'how': '株元に少量与えます。', 'product_name': 'ピーマン・パプリカの肥料', 'affiliate_link': 'https://amzn.to/4kl8ldT', 'recommendation_reason': '液体肥料は即効性があり、すぐに栄養を届けたいこの時期にぴったりです。'},
            {'gdd': 900, 'advice': '実がなり始めました。', 'what': '水やり管理', 'how': '乾燥に注意し、水やりを欠かさないようにしましょう。'}
        ]
    },
    'えだまめ': {
        'base_temp': 10.0, 'image_url': 'https://images.pexels.com/photos/2551790/pexels-photo-2551790.jpeg', 'avg_gdd_per_day': 18,
        'initial_products': [
            {'name': '豆類専用の肥料', 'link': 'https://amzn.to/3TfX1EP', 'reason': 'えだまめの生育に必要な栄養素をバランスよく含んでいます。'},
        ],
        'events': [
            {'gdd': 250, 'advice': '花が咲き始めたら、追肥のタイミングです。', 'what': 'リン酸・カリウムが多めの肥料', 'how': '窒素分が多いと葉ばかり茂るので注意。株元に軽く一握り与えましょう。', 'product_name': '豆類専用の肥料', 'affiliate_link': 'https://amzn.to/3TfX1EP', 'recommendation_reason': 'えだまめは自分で窒素を作れるため、実や根の成長を助けるリン酸・カリウムが中心の肥料が効果的です。'},
            {'gdd': 600, 'advice': 'さやが膨らんできました！収穫が楽しみですね。', 'what': '水やり', 'how': '乾燥はさやの成長に影響します。特にこの時期は水を切らさないようにしましょう。'}
        ]
    },
    'しそ': {
        'base_temp': 15.0, 'image_url': 'https://images.pexels.com/photos/13532392/pexels-photo-13532392.jpeg', 'avg_gdd_per_day': 12,
        'initial_products': [
            {'name': 'しそ栽培キット', 'link': 'https://amzn.to/4c5hF3X', 'reason': '種と土、プランターがセットになっていて手軽に始められます。'},
        ],
        'events': [{'gdd': 150, 'advice': '本葉が10枚以上になったら、摘心（てきしん）をしましょう。', 'what': '一番上の芽', 'how': '先端をハサミでカットすると、脇芽が増えて収穫量がアップします。'}, {'gdd': 300, 'advice': '収穫が始まります！葉が茂ってきたら、2週間に1回程度の追肥を。', 'what': '液体肥料', 'how': '規定の倍率に薄めたものを、水やり代わりに与えると手軽です。'}]
    },
    'ミニダイコン': {
        'base_temp': 5.0,
        'image_url': 'https://images.pexels.com/photos/14982333/pexels-photo-14982333.jpeg',
        'avg_gdd_per_day': 11,
        'initial_products': [
            {'name': '深型プランター (20cm以上)', 'link': 'https://amzn.to/3Xp5sJq', 'reason': 'ミニでも根は深く伸びます。十分な深さを確保することが、まっすぐなダイコンを育てる秘訣です。'},
            {'name': 'かるいプランターの土', 'link': 'https://amzn.to/3VEzW1W', 'reason': '水はけの良い、ふかふかの土がダイコンのベッドに最適です。'}
        ],
        'events': [
            {'gdd': 130, 'advice': '間引きのタイミングです！', 'what': '本葉が1〜2枚になったら、形の良いものを残して1本に絞ります。', 'how': '残す株を傷つけないよう、間引く株の根元をハサミで切り取るのが最も安全で確実な方法です。'},
            {'gdd': 280, 'advice': '追肥と土寄せを行いましょう。', 'what': '化成肥料を株元に与えます。', 'how': '肥料を撒いた後、ダイコンの根の白い部分（肩）が土から見えていたら、土を寄せて隠してあげましょう。光に当たると緑色になってしまいます。', 'product_name': '野菜用の化成肥料', 'affiliate_link': 'https://amzn.to/4c5kX7s', 'recommendation_reason': '根が太り始める重要な時期。栄養を補給し、美しいダイコンに育てましょう。'},
            {'gdd': 650, 'advice': 'いよいよ収穫です！', 'what': '土から出ている根の直径が5〜7cmになったら収穫の目安です。', 'how': '葉の付け根をしっかりと持ち、まっすぐ上に引き抜きます。収穫が遅れると「す」が入って食感が悪くなるので注意しましょう。'}
        ]
    },
    'タマネギ': {
        'base_temp': 4.0,
        'image_url': 'https://images.pexels.com/photos/144234/onions-kitchen-bio-food-144234.jpeg',
        'avg_gdd_per_day': 9,
        'initial_products': [
            {'name': 'ホームタマネギ (球根)', 'link': 'https://amzn.to/3VGfLzK', 'reason': '種から育てるより圧倒的に簡単で、失敗が少ないです。8月下旬から9月が植え付けのベストタイミング。'},
            {'name': '標準プランター', 'link': 'https://amzn.to/3RjV0gR', 'reason': '深さは15cmもあれば十分。株同士の間隔を10cmほどあけて植え付けます。'}
        ],
        'events': [
            {'gdd': 350, 'advice': '追肥のタイミングです。', 'what': '植え付けから約1ヶ月後、葉の色が薄くなってきたら追肥のサインです。', 'how': '株元に化成肥料をパラパラと撒き、土と軽く混ぜ合わせます。', 'product_name': '野菜用の化成肥料', 'affiliate_link': 'https://amzn.to/4c5kX7s', 'recommendation_reason': '球が大きくなり始めるためのエネルギーを補給します。この追肥が、玉の大きさを左右します。'},
            {'gdd': 800, 'advice': '収穫のサインを見逃すな！', 'what': '全体の7〜8割の葉が自然に倒れたら、それが収穫の合図です。', 'how': '晴れた日を選んで、株を引き抜きます。収穫後、葉を付けたまま2〜3日、畑で乾燥させると長持ちします。'}
        ]
    },
    'ミニハクサイ': {
        'base_temp': 5.0,
        'image_url': 'https://images.pexels.com/photos/5443209/pexels-photo-5443209.jpeg',
        'avg_gdd_per_day': 13,
        'initial_products': [
            {'name': 'ミニハクサイの種', 'link': 'https://amzn.to/4eiy4pS', 'reason': '通常のハクサイより結球しやすく、プランターでも60〜70日で収穫できるため初心者におすすめです。'},
            {'name': '防虫ネット', 'link': 'https://amzn.to/3VEA7hV', 'reason': 'アオムシなどの害虫から柔らかい葉を守るための必須アイテム。トンネル支柱とセットで使いましょう。'}
        ],
        'events': [
            {'gdd': 300, 'advice': '追肥と土寄せの時期です。', 'what': '本葉が5〜6枚になったら、化成肥料を追肥します。', 'how': '肥料を株の周りに撒き、株が倒れないように根元に軽く土を寄せてあげます。'},
            {'gdd': 700, 'advice': '結球を助けるひと手間！', 'what': '葉が巻いて球になり始めたら、外側の葉で球を包むように、紐などで軽く縛ってあげます。', 'how': 'こうすることで、葉が綺麗に巻き、締まりの良いハクサイになります。'},
            {'gdd': 1000, 'advice': '収穫のタイミングです。', 'what': '球の上部を手で軽く押してみて、固く締まっていたら収穫できます。', 'how': '株元に包丁を入れて、根を切り離して収穫します。'}
        ]
    },
    'ニンジン': {
        'base_temp': 5.0,
        'image_url': 'https://images.pexels.com/photos/143133/pexels-photo-143133.jpeg',
        'avg_gdd_per_day': 14,
        'initial_products': [
            {'name': '深型プランター (30cm以上)', 'link': 'https://amzn.to/3Xp5sJq', 'reason': 'ニンジンをまっすぐ育てるには、根が伸びるための十分な深さが必要です。'},
            {'name': 'ニンジンの種', 'link': 'https://amzn.to/3VHj53D', 'reason': 'プランターなら「ベビーキャロット」のような短い品種が育てやすいです。'}
        ],
        'events': [
            {'gdd': 200, 'advice': '最重要！発芽後の間引き。', 'what': '本葉が2〜3枚の頃に1回目の間引きを行い、株間を3cm程度にします。', 'how': '本葉が5〜6枚になったら2回目の間引きを行い、最終的な株間を10〜12cmにします。間引きが遅れると根が曲がる原因になります。'},
            {'gdd': 450, 'advice': '追肥と土寄せで、肩の日焼けを防ぐ！', 'what': '2回目の間引きが終わったら、追肥を行います。', 'how': 'ニンジンの根の上部（肩）が見えていたら、土を寄せて隠しましょう。光に当たると緑化してしまいます。', 'product_name': '野菜用の化成肥料', 'affiliate_link': 'https://amzn.to/4c5kX7s', 'recommendation_reason': '根が本格的に太り始める時期です。栄養補給と土寄せで、品質を向上させましょう。'},
            {'gdd': 1200, 'advice': '収穫の目安を確認しよう。', 'what': '土から見えている根の直径が、品種に適した太さになったら収穫です。', 'how': '試しに1本抜いてみて、太さを確認するのが確実です。収穫が遅れると根が割れやすくなります。'}
        ]
    },
    'ブロッコリー': {
        'base_temp': 5.0,
        'image_url': 'https://images.pexels.com/photos/4054358/pexels-photo-4054358.jpeg',
        'avg_gdd_per_day': 15,
        'initial_products': [
            {'name': 'ブロッコリーの苗', 'link': 'https://amzn.to/3VDEm0c', 'reason': '種から育てるのは難易度が高いため、初心者は苗から始めるのが確実です。'},
            {'name': '防虫ネットと支柱セット', 'link': 'https://amzn.to/3VEA7hV', 'reason': 'モンシロチョウなどの産卵を防ぎ、アオムシの被害を劇的に減らせます。ブロッコリー栽培の成功は、これがあるかないかで決まります。'}
        ],
        'events': [
            {'gdd': 350, 'advice': '追肥で株を大きく育てよう。', 'what': '植え付けから2週間後、化成肥料で1回目の追肥をします。', 'how': '株の周りに肥料を撒き、土と軽く混ぜて株元に土寄せします。'},
            {'gdd': 700, 'advice': '花蕾（からい）が見えたら2回目の追肥！', 'what': '中心にブロッコリーの蕾（花蕾）が見え始めたら、2回目の追肥を行います。', 'how': 'これが最後の追肥です。この栄養が、ブロッコリーの大きさと味を決めます。', 'product_name': '野菜用の化成肥料', 'affiliate_link': 'https://amzn.to/4c5kX7s', 'recommendation_reason': '花蕾を大きく育てるための最後の栄養補給です。忘れずに行いましょう。'},
            {'gdd': 1100, 'advice': '収穫のベストタイミング！', 'what': '花蕾が直径10〜15cmになり、固く締まっていたら収穫です。', 'how': '蕾が黄色くなる前に、茎を長めに付けて切り取ります。収穫後、脇から出てくる蕾（側花蕾）も、小さいですが収穫して楽しめます。'}
        ]
    }
}