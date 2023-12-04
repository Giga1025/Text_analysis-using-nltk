import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re


df = pd.read_excel("C:/Users/byash/Downloads/drive-download-20231105T063212Z-001/Output Data Structure.xlsx")

df1 = df.copy()
i = 0
for index,row in df.iterrows():
    if index == i and row["URL"]:
        URL = row["URL"]
        try:
            response = requests.get(URL)
            response.raise_for_status()
            response = response.text
            
            soup = BeautifulSoup(response, "html.parser")

            df1 = []
            title = soup.find("title")
            cleaned_title = title.text.replace(" - Blackcoffer Insights", "")
            df1.append(cleaned_title.upper())
            content = []
            for para in soup.find_all("p", class_ = ""):
                content.append(para.text.upper())
            combined_text = ' '.join(content)

            if combined_text is None or combined_text.strip() == "":
                # If combined_text is None or empty, try another class
                content = []  # Clear the content list
                for para in soup.find_all("p", class_ = "has-text-align-left"):
                    content.append(para.text.upper())
                combined_text = ' '.join(content)

            df1.append(combined_text)
            text_tok = " ".join(df1)

            with open(f"url_{row['URL_ID']}.txt", 'w', encoding='utf-8') as url:

                url.write(text_tok)
            print(f"Data saved to url_{row['URL_ID']}.txt")

            #SENTENCE COUNT
            from nltk import word_tokenize
            sen = []
            for para in soup.find_all("p", class_ = ""):
                sen.append(para.text.upper())
            str_sen = ' '.join(sen)

            if str_sen is None or str_sen.strip() == "":
                # If combined_text is None or empty, try another class
                sen = []  # Clear the content list
                for para in soup.find_all("p", class_ = "has-text-align-left"):
                    sen.append(para.text.upper())
                str_sen = ' '.join(content)
            sen_word = word_tokenize(str_sen)

            sen_count = 0
            for word in sen_word:
              if word== "." or word=="?":
                sen_count+=1
            sen_count

            #Stop words

            with open("C:/Users/byash/Downloads/stop_words/StopWords_Generic.txt", 'r' ) as file:
                Generic_sw = [word.strip() for word in file]
            with open("C:/Users/byash/Downloads/stop_words/StopWords_Auditor.txt", 'r') as fileA:
                Auditor_sw = [word.strip() for word in fileA]
            with open("C:/Users/byash/Downloads/stop_words/StopWords_DatesandNumbers.txt", 'r') as fileD:
                DatesnNumbers_sw = [word.strip() for word in fileD]
            with open("C:/Users/byash/Downloads/stop_words/StopWords_GenericLong.txt",'r') as fileG:
                Generic_long_sw = [word.strip() for word in fileG]
            with open("C:/Users/byash/Downloads/stop_words/StopWords_Geographic.txt", 'r') as fileGE:
                Geo_sw = [word.strip() for word in fileGE]
            with open("C:/Users/byash/Downloads/stop_words/StopWords_Names.txt",'r') as fileN:
                Names_sw = [word.strip() for word in fileN]
            with open("C:/Users/byash/Downloads/stop_words/StopWords_Currencies.txt", 'r') as fileC:
                Currencies_sw = [word.strip() for word in fileC]
            Currencies_sw = [word.split('|')[0].strip() for word in Currencies_sw]

            mis = [',', '?', '!', '.']

            #print(f"Generic: {Generic_sw}\nAuditor: {Auditor_sw}\nDatesandnumbers: {DatesnNumbers_sw}\nGenericlong: {Generic_long_sw}\nGeo: {Geo_sw}\nNames: {Names_sw}\nCurriencies: {Currencies_sw}")

            All_sw = Generic_sw+Auditor_sw+DatesnNumbers_sw+Generic_sw+Geo_sw+Names_sw+Currencies_sw+mis

            # Negative and Positive words
            with open("C:/Users/byash/Downloads/Master_dictionary/positive-words.txt",'r') as fileP:
                Positive_mw = [word.strip().upper() for word in fileP]
            with open("C:/Users/byash/Downloads/Master_dictionary/negative-words.txt",'r') as fileN:
                Negative_mw = [word.strip().upper() for word in fileN]

            
            #Tokenaizing
            words = word_tokenize(text_tok)
            words_wout_title = word_tokenize(str_sen)
            str_words = " ".join(words_wout_title)

            #Word count

            stripped_phrase = []
            for word in words:
                if word not in All_sw:
                    stripped_phrase.append(word)
                    
            stripped_wout_title = []
            for word in words_wout_title:
                if word not in All_sw:
                    stripped_wout_title.append(word)

            len_after_cleaning = len(stripped_phrase)
            len_wout_title_cleaned = len(stripped_wout_title)
            joined = " ".join(stripped_wout_title)
            df.at[index , "WORD COUNT"] = len_wout_title_cleaned

            # Polarity

            positive, negative = 0, 0

            for word in words:
                if word in Positive_mw:
                    positive += 1
                elif word in Negative_mw:
                    negative += 1
            df.at[index, "POSITIVE SCORE"] = positive
            df.at[index, "NEGATIVE SCORE"] = negative
            

            polarity = (positive - negative) / ((positive + negative) + 0.000001)
            df.at[index, "POLARITY SCORE"] = polarity

            # Subjective score

            s_score = (positive+negative)/ (len_after_cleaning+0.000001)
            df.at[index, "SUBJECTIVITY SCORE"] = s_score
            print(s_score)

            #Average sentence length
            asl = len_wout_title_cleaned/ sen_count
            df.at[index, "AVG SENTENCE LENGTH"] = asl
            df.at[index, "AVG NUMBER OF WORDS PER SENTENCE"] = asl
            
            
            #Syllables
            countn = 0
            vowels = "AEIOUaeiou"
            for word in stripped_wout_title:
                if not (word.endswith("ES") or word.endswith("ED")):
                    for letter in word:
                        if letter in vowels:
                            countn += 1

            syllables_per_word = countn/ len_wout_title_cleaned 
            df.at[index, "SYLLABLE PER WORD"] = syllables_per_word

            # COMPLEX WORDS
            count= 0
            vowels = "AEIOUaeiou"
            words_with_more_than_two_vowels = []

            for word in stripped_wout_title:
                vowel_count = sum(1 for letter in word if letter in vowels)
                if vowel_count > 2 and not (word.endswith("ES") or word.endswith("ED")):
                    words_with_more_than_two_vowels.append(word)

            #print("Words with more than two vowels:", words_with_more_than_two_vowels)
            complex_count = len(words_with_more_than_two_vowels)
            df.at[index, "COMPLEX WORD COUNT"] = complex_count


            #PERCENTAGE OF COMPLEX WORDS

            percentage_of_complex_words = len(words_with_more_than_two_vowels)/ len_wout_title_cleaned
            df.at[index, "PERCENTAGE OF COMPLEX WORDS"] = percentage_of_complex_words
            # FOG INDEX

            Fog_index = 0.4* (asl+percentage_of_complex_words)
            df.at[index,"FOG INDEX"] = Fog_index

            # PERSONAL PRONOUNS

            pronounRegex = re.compile(r'\b(I|WE|MY|OURS|(?-i:US))\b',re.I)
            personal_pronoun = pronounRegex.findall(str_words)
            personal_pro_len = len(personal_pronoun)
            df.at[index, "PERSONAL PRONOUNS"] = personal_pro_len

            # AVERAGE WORD LENGTH

            countA = 0
            for word in stripped_wout_title:
                for char in word:
                    countA+=1

            AWL = countA/ len_wout_title_cleaned
            df.at[index, "AVG WORD LENGTH"] = AWL
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        
    i+=1


df.to_excel('C:/Users/byash/OneDrive/Desktop/New folder/Output_excel_.xlsx', index=False)  # Save as CSV without including the index














        


