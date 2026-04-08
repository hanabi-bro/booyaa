def parse_text(text):
    """
    テキストを解析し、ネストされたリストに変換する関数

    Args:
        text: 解析対象のテキスト

    Returns:
        list: ネストされたリスト
    """

    lines = text.splitlines()
    result = []
    current_list = result
    indent_level = 0

    for line in lines:
        # 行頭の空白文字数をカウントしてインデントレベルを算出
        indent = len(line) - len(line.lstrip())
        # インデントレベルが減った場合は、上位のリストに戻る
        while indent < indent_level:
            current_list = current_list[-1]
            indent_level -= 1
        # 空白を除去して単語のリストを作成
        words = line.strip().split()
        # 新しいリストを作成するか、既存のリストに単語を追加
        if indent == indent_level:
            current_list.append(words)
        else:
            new_list = []
            current_list.append(new_list)
            current_list = new_list
        indent_level = indent

    return result
