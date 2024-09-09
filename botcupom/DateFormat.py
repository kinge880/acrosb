def dateFormat(date):
    
    if date != '':
        dates = {
            '01': 'JAN',
            '02': 'FEB',
            '03': 'MAR',
            '04': 'APR',
            '05': 'MAY',
            '06': 'JUN',
            '07': 'JUL',
            '08': 'AUG',
            '09': 'SEP',
            '10': 'OCT',
            '11': 'NOV',
            '12': 'DEC'
        }
        
        formatDate= str(date).split('-')
        formatMonth = dates[formatDate[1]]
        formatDate = '{}-{}-{}'.format(formatDate[2],formatMonth,formatDate[0])
        return(formatDate)
    else:
        return ''