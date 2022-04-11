# dependencies

# function to find experience requirement (I search for entry-level jobs, i.e. 0 years of experience)
def expReq(job_descr):
    
    # check whether 'experience' occurs in job_descr
    if job_descr.find('experience') < 0:
        return(0)
    
    ### find all occurences of 'experience' (inefficient but works)
    exp_list = [i for i in range(len(job_descr)) if job_descr.startswith('experience', i)]
    
    # empty list to store sentences with 'experience'
    exp_sentences = []
    
    # search for whole sentence with 'experience'
    for index in exp_list:
        # iterate backwards until ';', which marks sentence start is found
        i = index
        while job_descr[i] != ';':
            if i == 0:
                break
            sentence_start = i
            i = i-1
           
        
        # iterate forward until '&', which marks sentence end is found
        j = index
        while job_descr[j] != '&':
            j = j+1
            sentence_end = j
            if j == len(job_descr):
                break
        
        exp_sentences.append(job_descr[sentence_start:sentence_end])
    
    ### find experience requirement
    # empty list to store experience req.
    sentences_exp_req = []

    for sent in exp_sentences:
    
        # check if string contains any integers
        if any(char.isdigit() for char in sent) == False:
            sentences_exp_req.append(0)
            continue
        
        # find integer
        req = int(re.search(r'\d+', sent).group())
        
        # if 'too large', return 0
        if req > 20:
            req = 0
        sentences_exp_req.append(req)
    
    # find max and index
    exp_req = max(sentences_exp_req) 
        
    exp_req_index = sentences_exp_req.index(exp_req)
    
    ### look for keywords that indicate that experience is preferable, ideal, etc.
    # set keywords
    exp_keywords = ['preferably', 'ideal', 'ideally', 'less']

def scrapeLinkedIn(positionName):
    
    name_wo_space = positionName.replace(' ', '%20')
    
    #set url and request page
    url = f"https://www.linkedin.com/jobs/search/?f_AL=true&f_TPR=r2592000&geoId=92000000&keywords={name_wo_space}&location=Hele%20verden&sortBy=DD"
    page = requests.get(url)
    
    # empty lists for info
    titles = []
    companies = []
    locations = []
    links = []
    job_dates = []
    isEA = []
    exp_reqs = []
    
    # fill lists
    jobNumber = 0
    while jobNumber <= 1000:
        
        # if first page use original url
        if jobNumber < 25:
            new_url = url
            
        # if greater than first page add appropraite suffix
        new_url = url+f"&start={jobNumber}"
        
        page = requests.get(new_url)
    
        # parse html code with beautifulsoup
        soup = bs(page.content, "html.parser")
                
        # check if element has the attribute find_all - skip if not
        if not hasattr(soup.find("body"), 'find_all'):
            continue
            
        uls = soup.find("body").find_all("h3", class_="base-search-card__title")
        
        # find great-grandparent elements to access all info
        job_elements = [
            h3_element.parent.parent.parent for h3_element in uls
        ]
        
        for job_element in job_elements:
            titles.append(job_element.find("h3", class_="base-search-card__title").text.strip())
            companies.append(job_element.find("h4", class_="base-search-card__subtitle").text.strip())
            locations.append(job_element.find("span", class_="job-search-card__location").text.strip())
            links.append(job_element.find_all("a")[0]["href"]) # choose second link (apply link)
        
        jobNumber = jobNumber + 25
    
    # scrape info from each link
    for link in links:
        page = requests.get(link)
        
         # parse html code with beautifulsoup
        soup = bs(page.content, "html.parser")
        
        ### find json element of application: contains date posted, description, etc.
        job_info = soup.find_all("script", type="application/ld+json")
        
        # might be empty, so check whether it exists, and return arbitrary date otherwise
        if bool(job_info) == True: 
            job_info = soup.find_all("script", type="application/ld+json")[0]
            # load using json, cut after 10th character (post time irrelevant)
            job_date = json.loads(job_info.text)['datePosted'][:10]
            
            # load job descr. using json and find exp_req with expReq function
            job_descr = json.loads(job_info.text)['description']
            exp_req = expReq(job_descr)
        else:
            # set arbitrary date
            job_date = "2000-01-01"
            exp_req = 0
        
        # find easy apply button, return false if list empty
        easy_apply = soup.find_all("button", class_="apply-button apply-button--default top-card-layout__cta top-card-layout__cta--primary")
        easy_apply = bool(easy_apply)
        
        job_dates.append(job_date)
        isEA.append(easy_apply)
        exp_reqs.append(exp_req)
        
    # print csv file with info
    df_jobs = pd.DataFrame(list(zip(titles, companies, locations, isEA, exp_reqs, job_dates, links)),
                      columns = ["title", "company", "location", "easy_apply", "exp_req", "posted_on", "url"])
    
    df_jobs.drop_duplicates(subset=['title', 'company', 'location', "posted_on"], keep='last', inplace=True)
    path = 'C:\\Users\\rasmu\\OneDrive\\Dokumenter\\Rasmus - diverse\\Jobansøgninger'
    os.chdir(path)
    df_jobs.to_csv(positionName + '_list_of_jobs.csv')
    
    return(df_jobs)
    
    # loop through keywords and add to count
    count = 0
    for key in exp_keywords:
        # check if key is in exp-string (converted to lower case)
        count = count + int(exp_sentences[exp_req_index].lower().find(key)>-1)
        
    if count > 0: exp_req = 0
    
    return(exp_req)
    
 
