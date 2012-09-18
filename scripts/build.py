def parse_file(input_file_path):
    f = open(input_file_path)

    # array listing all the experiences
    exps = []

    #loop over experiences
    line = f.readline()
    while line:
        if line.strip() == '###':
            exp = {'title': f.readline().strip(), 'subtitle': f.readline().strip(), 'type': f.readline().strip(), 'date': f.readline().strip()}
            description = f.readline().strip()
            next_line = f.readline()
            while next_line[0:2] == '  ':
                description += ' ' + next_line.strip()
                next_line = f.readline()
            exp['description'] = description
            exp['keywords'] = next_line.strip().split(',')
            exps.append(exp)
        line = f.readline()

    #print results
    # for exp in exps:
    #     print "###"
    #     print exp['title'] + exp['subtitle'] +  exp['type'] + exp['year'] + exp['description'] + exp['keywords']

    # read the template file
    o = open("experience-template.html")
    template = o.read()

    # increment template with each experience
    exp_cpt = 0
    exp_html = ''
    for exp in exps:
        inc_template = template.replace('%TITLE%', exp['title'])
        inc_template = inc_template.replace('%SUBTITLE%', exp['subtitle'])
        inc_template = inc_template.replace('%DATE%', exp['date'])
        inc_template = inc_template.replace('%TYPE%', exp['type'])
        inc_template = inc_template.replace('%DESCRIPTION%', exp['description'])
        even_odd_str = 'odd'
        if exp_cpt % 2 == 0:
            even_odd_str = 'even'
        inc_template = inc_template.replace('%EVEN_ODD%', even_odd_str)
        exp_cpt += 1
        exp_html += inc_template

    inc_layout = exp_html

    # read the layout file
    layout_file = open("layout.html")
    layout = layout_file.read()
    inc_layout = layout.replace('%EXPERIENCES%', exp_html)

    # open the output file
    index_file = open("index.html", "w")
    index_file.write(inc_layout)

parse_file("experiences.textdb")
