# plant_data.py
PLANT_DATABASE = {
    'ベビーリーフ': {
        'category': '秋冬野菜', 'popularity': 1, 'base_temp': 5.0, 'image_url': 'https://t4.ftcdn.net/jpg/00/77/96/89/240_F_77968929_IHVqfnPi8Sywkb3Ket5NBRdHFl7r9z7I.jpg', 'avg_gdd_per_day': 9,
        'watering_freq': '土の表面が乾いたら、鉢底から水が出るまでたっぷりと。霧吹きで葉に水をかけるのも効果的です。', 'fertilizer_freq': '2〜3回摘み取って収穫した後、葉の色が薄くなってきたら液体肥料を与えます。',
        'recurring_consumables': [{'name': '速効性のある液体肥料', 'link': 'https://amzn.to/4n1KIc0', 'reason': '継続的に収穫するためには、定期的な栄養補給が不可欠。即効性のある液体肥料が最適です。'}, {'name': '有機野菜の土', 'link': 'https://amzn.to/45CLdDF', 'reason': '次の栽培の準備に。新しい土で連作障害を防ぎましょう。'}],
        'events': [{'gdd': 200, 'advice': '収穫を開始できます！', 'what': '草丈が10cm程度になったら、いつでも収穫可能です。', 'how': '外側の葉から、必要な分だけハサミで切り取って収穫します。中心の新しい葉を残しておけば、次々と新しい葉が出てきて、長期間収穫を楽しめます。'}, {'gdd': 350, 'advice': '元気がなくなってきたら追肥を。', 'what': '2〜3回ほど収穫した後、葉の色が薄くなってきたら追肥のサインです。', 'how': '薄めた液体肥料を、水やり代わりに週に1回程度与えましょう。', 'product_name': '速効性のある液体肥料', 'affiliate_link': 'https://amzn.to/4n1KIc0', 'recommendation_reason': '継続的に収穫するためには、定期的な栄養補給が不可欠。即効性のある液体肥料が最適です。'}]
    },
    'コマツナ': {
        'category': '秋冬野菜', 'popularity': 2, 'base_temp': 5.0, 'image_url': 'https://t4.ftcdn.net/jpg/04/81/34/17/240_F_481341790_wly5cGVM4xj1llANj36hDaxMzJzVLEHh.jpg', 'avg_gdd_per_day': 10,
        'watering_freq': '土の表面が乾いたらたっぷりと。特に発芽までは土を乾かさないように注意が必要です。', 'fertilizer_freq': '本葉が4〜5枚になったら、2週間に1回のペースで追肥します。',
        'recurring_consumables': [{'name': '野菜用の液体肥料', 'link': 'https://amzn.to/4n1KIc0', 'reason': '葉を大きく育てるために、定期的な栄養補給が効果的です。'}, {'name': '防虫ネット', 'link': 'https://amzn.to/4oVXWsy', 'reason': 'アオムシなどの害虫は、ネットで物理的に防ぐのが最も安全で確実です。'}],
        'events': [{'gdd': 120, 'advice': '間引きのタイミングです！', 'what': '混み合った部分の苗を、指でつまんで根元からそっと引き抜きます。', 'how': '本葉が1〜2枚の頃が目安。株同士の間隔が3cm程度になるように調整しましょう。良い苗を残すのがコツです。'}, {'gdd': 250, 'advice': '最初の追肥を行いましょう！', 'what': '液体肥料、または化成肥料がおすすめです。', 'how': '液体肥料なら週に1回、水やり代わりに。化成肥料なら、株元にパラパラと撒き、土と軽く混ぜ合わせます。', 'product_name': '野菜用の液体肥料', 'affiliate_link': 'https://amzn.to/4n1KIc0', 'recommendation_reason': 'ここからの成長が著しい時期。栄養をしっかり与えることで、葉が大きく肉厚になります。'}, {'gdd': 450, 'advice': '収穫の時期です！', 'what': '草丈が20〜25cmになったら収穫の合図です。', 'how': '株元をハサミで切り取るか、根元から引き抜いて収穫します。大きく育ったものから順に収穫すると、長く楽しめます。'}]
    },
    'ミニダイコン': {
        'category': '秋冬野菜', 'popularity': 3, 'base_temp': 5.0, 'image_url': 'https://t4.ftcdn.net/jpg/00/28/09/23/240_F_28092323_SJgNJkg1aZ1ltyte7fdIwEzDf8cLV6Ln.jpg', 'avg_gdd_per_day': 11,
        'watering_freq': '土の表面が乾いたら、たっぷりと与えます。根が太り始めたら、乾燥させすぎないように注意。', 'fertilizer_freq': '間引きが終わった後、2週間に1回のペースで追肥します。',
        'recurring_consumables': [{'name': '野菜用の化成肥料', 'link': 'https://amzn.to/4lNn4iw', 'reason': '根を太らせるためには、定期的な追肥が欠かせません。'}, {'name': '防虫ネット', 'link': 'https://amzn.to/4oVXWsy', 'reason': 'アブラムシやコナガから葉を守り、健康な株を維持します。'}],
        'events': [{'gdd': 130, 'advice': '間引きのタイミングです！', 'what': '本葉が1〜2枚になったら、形の良いものを残して1本に絞ります。', 'how': '残す株を傷つけないよう、間引く株の根元をハサミで切り取るのが最も安全で確実な方法です。'}, {'gdd': 280, 'advice': '追肥と土寄せを行いましょう。', 'what': '化成肥料を株元に与えます。', 'how': '肥料を撒いた後、ダイコンの根の白い部分（肩）が土から見えていたら、土を寄せて隠してあげましょう。光に当たると緑色になってしまいます。', 'product_name': '野菜用の化成肥料', 'affiliate_link': 'https://amzn.to/4lNn4iw', 'recommendation_reason': '根が太り始める重要な時期。栄養を補給し、美しいダイコンに育てましょう。'}, {'gdd': 650, 'advice': 'いよいよ収穫です！', 'what': '土から出ている根の直径が5〜7cmになったら収穫の目安です。', 'how': '葉の付け根をしっかりと持ち、まっすぐ上に引き抜きます。収穫が遅れると「す」が入って食感が悪くなるので注意しましょう。'}]
    },
    '小カブ': {
        'category': '秋冬野菜', 'popularity': 4, 'base_temp': 5.0, 'image_url': 'https://t3.ftcdn.net/jpg/01/21/28/84/240_F_121288401_kYk3S9OX7lvBlMuqlKjjjxX8SKz2aGYB.jpg', 'avg_gdd_per_day': 12,
        'watering_freq': '乾燥に弱いので、土の表面が乾いたら必ず水をやりましょう。特に根が大きくなる時期は重要です。', 'fertilizer_freq': '2回目の間引きの後と、根が太り始める頃の計2回、追肥を行います。',
        'recurring_consumables': [{'name': '野菜用の化成肥料', 'link': 'https://amzn.to/4lNn4iw', 'reason': '根を甘く、大きく育てるための追肥は必須です。'}, {'name': '防虫ネット', 'link': 'https://amzn.to/4oVXWsy', 'reason': 'カブの葉は虫に好かれやすいので、ネットでしっかりガードしましょう。'}],
        'events': [{'gdd': 150, 'advice': '間引きの時期です。', 'what': '双葉が開いたら最初の間引き。形の良いものを残し、3cm間隔にします。', 'how': '本葉が2〜3枚になったら2回目の間引きを行い、最終的に株間を10cm程度に広げます。'}, {'gdd': 300, 'advice': '追肥と土寄せをしましょう。', 'what': '化成肥料を株元に与えます。', 'how': '肥料を与えた後、カブの根元が少し膨らんできたら、肩の部分に土を寄せてあげます。こうすることで、形が良く、きれいなカブに育ちます。', 'product_name': '野菜用の化成肥料', 'affiliate_link': 'https://amzn.to/4lNn4iw', 'recommendation_reason': '根が大きくなり始める、最も栄養が必要なタイミングです。しっかり追肥しましょう。'}, {'gdd': 600, 'advice': '収穫のタイミングです！', 'what': '根の直径が5〜6cmになったら収穫しましょう。', 'how': '葉の付け根を持って、まっすぐ上に引き抜きます。収穫が遅れると、根が割れてしまう（裂根）ことがあるので注意が必要です。'}]
    },
    'ミニトマト': {
        'category': '夏野菜', 'popularity': 6, 'base_temp': 10.0, 'image_url': 'https://images.pexels.com/photos/7208483/pexels-photo-7208483.jpeg', 'avg_gdd_per_day': 15,
        'watering_freq': '土の表面が乾いたら、鉢底から水が流れ出るまでたっぷりと。夏場は朝夕2回必要なことも。', 'fertilizer_freq': '最初の実がつき始めたら、2週間に1回のペースで追肥します。',
        'recurring_consumables': [{'name': 'トマトの追肥用肥料', 'link': 'https://amzn.to/41quvox', 'reason': '実をつけ続けるために、栄養豊富な追肥は欠かせません。'}, {'name': '病害虫対策スプレー', 'link': 'https://amzn.to/46am6YQ', 'reason': 'アブラムシやうどんこ病の予防と対策に。一本あると安心です。'}],
        'events': [{'gdd': 300, 'advice': '最初の追肥のタイミングです！', 'what': '栄養バランスの良い、野菜用の肥料がおすすめです。', 'how': '一株あたり約10g（大さじ1杯程度）を、株元から少し離して円を描くように与えます。', 'product_name': 'トマトの追肥用肥料', 'affiliate_link': 'https://amzn.to/41quvox', 'recommendation_reason': '実をつけ始める大切な時期。バランスの取れた栄養が、甘くて美味しいトマトを育てる秘訣です。'}, {'gdd': 900, 'advice': '収穫まであと少し！', 'what': '水やりを管理しましょう。', 'how': '土の表面が乾いたら、朝のうちにたっぷりと。実が赤くなり始めたら、少し乾燥気味にすると糖度が上がります。'}]
    },
    'きゅうり': {
        'category': '夏野菜', 'popularity': 7, 'base_temp': 12.0, 'image_url': 'https://images.pexels.com/photos/7543157/pexels-photo-7543157.jpeg', 'avg_gdd_per_day': 20,
        'watering_freq': '乾燥に弱いので、土の表面が乾いたら毎日たっぷりと。特に夏場は水切れに注意。', 'fertilizer_freq': '実がなり始めたら、1週間に1回のペースで追肥を続けると、長く収穫できます。',
        'recurring_consumables': [{'name': 'きゅうりの肥料', 'link': 'https://amzn.to/4oVqxy4', 'reason': '生育が早く栄養を大量に消費するため、定期的な追肥が収穫量を左右します。'}, {'name': '野菜用 活力剤', 'link': 'https://amzn.to/4lJhZaZ', 'reason': '生育が悪い時や、葉の色が薄い時に使うと元気になります。'}],
        'events': [{'gdd': 250, 'advice': '最初の追肥のタイミングです。', 'what': '化成肥料を使いましょう。', 'how': '株元にパラパラと少量まき、土と軽く混ぜ合わせます。', 'product_name': 'きゅうりの肥料', 'affiliate_link': 'https://amzn.to/4oVqxy4', 'recommendation_reason': '生育が早い分、たくさんの栄養を必要とします。専用の肥料で元気に育てましょう。'}]
    },
    'えだまめ': {
        'category': '夏野菜', 'popularity': 8, 'base_temp': 10.0, 'image_url': 'https://images.pexels.com/photos/3298686/pexels-photo-3298686.jpeg', 'avg_gdd_per_day': 18,
        'watering_freq': '開花期からさやが膨らむ時期は、特に水を必要とします。土が乾いたらたっぷりと。', 'fertilizer_freq': '花が咲き始めたら一度だけ追肥します。窒素分が多いと葉ばかり茂るので注意。',
        'recurring_consumables': [{'name': '豆類専用の肥料', 'link': 'https://amzn.to/47N4mnx', 'reason': '実入りを良くするために、リン酸・カリウムが豊富な肥料を使いましょう。'}, {'name': '防虫ネット', 'link': 'https://amzn.to/4oVXWsy', 'reason': 'カメムシなどの害虫から、大事な実を守るために有効です。'}],
        'events': [{'gdd': 250, 'advice': '花が咲いたら、追肥の合図！', 'what': 'リン酸・カリウムが多めの肥料を使いましょう。', 'how': '窒素分が多いと葉ばかり茂るので注意。株元に軽く一握り与えましょう。', 'product_name': '豆類専用の肥料', 'affiliate_link': 'https://amzn.to/47N4mnx', 'recommendation_reason': 'えだまめは自分で窒素を作れるため、実や根の成長を助けるリン酸・カリウムが中心の肥料が効果的です。'}, {'gdd': 600, 'advice': 'さやが膨らんできました！', 'what': '水やりを忘れずに。', 'how': '乾燥はさやの成長に影響します。特にこの時期は水を切らさないようにしましょう。'}]
    },
    'なす': {
        'category': '夏野菜', 'popularity': 9, 'base_temp': 12.0, 'image_url': 'https://images.unsplash.com/photo-1639428134238-b548770d4b77?q=80&w=987&auto=format&fit=crop&ixlib.rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'avg_gdd_per_day': 18,
        'watering_freq': '「水で育つ」と言われるほど水を好みます。夏場は朝夕2回、たっぷりと与えましょう。', 'fertilizer_freq': '実がなり始めたら、2週間に1回のペースで追肥を続けます。',
        'recurring_consumables': [{'name': 'なす用の肥料', 'link': 'https://amzn.to/4mxxW4Z', 'reason': '長く収穫を楽しむ「秋なす」のためにも、肥料切れは絶対に避けましょう。'}, {'name': '支柱', 'link': 'https://amzn.to/45TdxjI', 'reason': '実が大きくなると重さで枝が折れることがあります。しっかりした支柱で支えましょう。'}],
        'events': [{'gdd': 350, 'advice': '最初の追肥のタイミングです。', 'what': '化成肥料を使いましょう。', 'how': '株の周りに円を描くように肥料を与えましょう。', 'product_name': 'なす用の肥料', 'affiliate_link': 'https://amzn.to/4mxxW4Z', 'recommendation_reason': '「なすは水と肥料で育つ」と言われるほど栄養が必要です。実をつけ続けるためのスタミナを補給しましょう。'}, {'gdd': 800, 'advice': '最初の実がなり始めました！', 'what': '継続的な追肥が必要です。', 'how': 'ここからは肥料切れに注意し、2週間に1回のペースで追肥を続けるのがおすすめです。'}]
    },
    'タマネギ': {
        'category': '秋冬野菜', 'popularity': 10, 'base_temp': 4.0, 'image_url': 'https://images.pexels.com/photos/175415/pexels-photo-175415.jpeg', 'avg_gdd_per_day': 9,
        'watering_freq': '過湿を嫌います。土の表面が乾いてから2〜3日後に水やりするくらいで十分です。', 'fertilizer_freq': '植え付けから1ヶ月後と、その1ヶ月後の計2回、追肥を行います。',
        'recurring_consumables': [{'name': '野菜用の化成肥料', 'link': 'https://amzn.to/4lNn4iw', 'reason': '玉ねぎを大きく、甘くするための重要な追肥です。'}, {'name': '有機石灰', 'link': 'https://amzn.to/41oXw3V', 'reason': '植え付け前に土に混ぜることで、土壌の酸度を調整し、生育を助けます。'}],
        'events': [{'gdd': 350, 'advice': '追肥のタイミングです。', 'what': '植え付けから約1ヶ月後、葉の色が薄くなってきたら追肥のサインです。', 'how': '株元に化成肥料をパラパラと撒き、土と軽く混ぜ合わせます。', 'product_name': '野菜用の化成肥料', 'affiliate_link': 'https://amzn.to/4lNn4iw', 'recommendation_reason': '球が大きくなり始めるためのエネルギーを補給します。この追肥が、玉の大きさを左右します。'}, {'gdd': 800, 'advice': '収穫のサインを見逃すな！', 'what': '全体の7〜8割の葉が自然に倒れたら、それが収穫の合図です。', 'how': '晴れた日を選んで、株を引き抜きます。収穫後、葉を付けたまま2〜3日、畑で乾燥させると長持ちします。'}]
    },
    'ピーマン': {
        'category': '夏野菜', 'popularity': 11, 'base_temp': 15.0, 'image_url': 'https://images.pexels.com/photos/4943441/pexels-photo-4943441.jpeg', 'avg_gdd_per_day': 16,
        'watering_freq': '乾燥に注意し、土の表面が乾いたらたっぷりと。水のやりすぎによる根腐れにも注意。', 'fertilizer_freq': '最初の実が確実についたら、2〜3週間に1回のペースで追肥します。',
        'recurring_consumables': [{'name': 'ピーマン・パプリカの肥料', 'link': 'https://amzn.to/4p0nhle', 'reason': '実を次々とならせるためには、定期的な栄養補給が鍵となります。'}, {'name': '支柱', 'link': 'https://amzn.to/45TdxjI', 'reason': 'たくさんの実がなると重くなるので、支柱でしっかりと支えてあげましょう。'}],
        'events': [{'gdd': 400, 'advice': '一番花が咲いたら追肥のサイン！', 'what': '化成肥料を使いましょう。', 'how': '株元に少量与えます。', 'product_name': 'ピーマン・パプリカの肥料', 'affiliate_link': 'https://amzn.to/4p0nhle', 'recommendation_reason': '液体肥料は即効性があり、すぐに栄養を届けたいこの時期にぴったりです。'}, {'gdd': 900, 'advice': '実がなり始めました。', 'what': '水やりを管理しましょう。', 'how': '乾燥に注意し、水やりを欠かさないようにしましょう。'}]
    },
    'ミニハクサイ': {
        'category': '秋冬野菜', 'popularity': 12, 'base_temp': 5.0, 'image_url': 'https://thumb.photo-ac.com/8a/8ae02c356fd4f5bc69bb39fbf736c875_t.jpeg', 'avg_gdd_per_day': 13,
        'watering_freq': '乾燥に弱いので、土の表面が乾いたらたっぷりと水を与えます。', 'fertilizer_freq': '植え付け2週間後と、その3週間後の計2回、追肥を行います。',
        'recurring_consumables': [{'name': '野菜用の化成肥料', 'link': 'https://amzn.to/4lNn4iw', 'reason': '葉がしっかりと巻く（結球する）ために、追肥で栄養を補いましょう。'}, {'name': '防虫ネット', 'link': 'https://amzn.to/4oVXWsy', 'reason': 'アオムシなどの害虫から柔らかい葉を守るための必須アイテムです。'}],
        'events': [{'gdd': 300, 'advice': '追肥と土寄せの時期です。', 'what': '本葉が5〜6枚になったら、化成肥料を追肥します。', 'how': '肥料を株の周りに撒き、株が倒れないように根元に軽く土を寄せてあげます。'}, {'gdd': 700, 'advice': '結球を助けるひと手間！', 'what': '葉が巻いて球になり始めたら、外側の葉で球を包むように、紐などで軽く縛ってあげます。', 'how': 'こうすることで、葉が綺麗に巻き、締まりの良いハクサイになります。'}, {'gdd': 1000, 'advice': '収穫のタイミングです。', 'what': '球の上部を手で軽く押してみて、固く締まっていたら収穫できます。', 'how': '株元に包丁を入れて、根を切り離して収穫します。'}]
    },
    'ブロッコリー': {
        'category': '秋冬野菜', 'popularity': 13, 'base_temp': 5.0, 'image_url': 'https://images.pexels.com/photos/1359326/pexels-photo-1359326.jpeg', 'avg_gdd_per_day': 15,
        'watering_freq': '土の表面が乾いたらたっぷりと。蕾（花蕾）が見え始めたら、特に水切れしないように注意。', 'fertilizer_freq': '植え付け2週間後と、蕾が見え始めた頃の計2回、追肥します。',
        'recurring_consumables': [{'name': '野菜用の化成肥料', 'link': 'https://amzn.to/4lNn4iw', 'reason': '頂花蕾（中心の蕾）と側花蕾（脇の蕾）の両方を収穫するために追肥は重要です。'}, {'name': '防虫ネット', 'link': 'https://amzn.to/4oVXWsy', 'reason': 'ブロッコリー栽培の成功は、アオムシ対策ができるかで決まります。'}],
        'events': [{'gdd': 350, 'advice': '追肥で株を大きく育てよう。', 'what': '植え付けから2週間後、化成肥料で1回目の追肥をします。', 'how': '株の周りに肥料を撒き、土と軽く混ぜて株元に土寄せします。'}, {'gdd': 700, 'advice': '花蕾（からい）が見えたら追肥！', 'what': '中心にブロッコリーの蕾（花蕾）が見え始めたら、2回目の追肥を行います。', 'how': 'これが最後の追肥です。この栄養が、ブロッコリーの大きさと味を決めます。', 'product_name': '野菜用の化成肥料', 'affiliate_link': 'https://amzn.to/4lNn4iw', 'recommendation_reason': '花蕾を大きく育てるための最後の栄養補給です。忘れずに行いましょう。'}, {'gdd': 1100, 'advice': '収穫のベストタイミング！', 'what': '花蕾が直径10〜15cmになり、固く締まっていたら収穫です。', 'how': '蕾が黄色くなる前に、茎を長めに付けて切り取ります。収穫後、脇から出てくる蕾（側花蕾）も、小さいですが収穫して楽しめます。'}]
    },
    'ニンジン': {
        'category': '秋冬野菜', 'popularity': 14, 'base_temp': 5.0, 'image_url': 'https://images.pexels.com/photos/1306559/pexels-photo-1306559.jpeg', 'avg_gdd_per_day': 14,
        'watering_freq': '発芽までが最も重要。種まき後は、土の表面が乾かないように毎日水やりします。', 'fertilizer_freq': '2回目の間引きの後と、その1ヶ月後の計2回、追肥を行います。',
        'recurring_consumables': [{'name': '野菜用の化成肥料', 'link': 'https://amzn.to/4lNn4iw', 'reason': '根をまっすぐ太く育てるために、定期的な栄養補給を行いましょう。'}, {'name': 'バーミキュライト', 'link': 'https://amzn.to/3UOTgae', 'reason': '種まき後、土の上に薄く覆うと、乾燥を防ぎ発芽率がアップします。'}],
        'events': [{'gdd': 200, 'advice': '最重要！発芽後の間引き。', 'what': '本葉が2〜3枚の頃に1回目の間引きを行い、株間を3cm程度にします。', 'how': '本葉が5〜6枚になったら2回目の間引きを行い、最終的な株間を10〜12cmにします。間引きが遅れると根が曲がる原因になります。'}, {'gdd': 450, 'advice': '追肥と土寄せで、肩の日焼けを防ぐ！', 'what': '2回目の間引きが終わったら、追肥を行います。', 'how': 'ニンジンの根の上部（肩）が見えていたら、土を寄せて隠しましょう。光に当たると緑化してしまいます。', 'product_name': '野菜用の化成肥料', 'affiliate_link': 'https://amzn.to/4lNn4iw', 'recommendation_reason': '根が本格的に太り始める時期です。栄養補給と土寄せで、品質を向上させましょう。'}, {'gdd': 1200, 'advice': '収穫の目安を確認しよう。', 'what': '土から見えている根の直径が、品種に適した太さになったら収穫です。', 'how': '試しに1本抜いてみて、太さを確認するのが確実です。収穫が遅れると根が割れやすくなります。'}]}
}