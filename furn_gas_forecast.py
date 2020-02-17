def furn_gas_forecast(H, distance, furn_id, *args, **kwargs):
    '''Прогнозирует поребление газа в печи ЛПЦ-10

    Args:
        H (pd.DataFrame): pandas-датафрейм с историческими данными по
        расходу газа с часовой детализацией
        distance (int): горизонт прогнозирования в часах
        furn_id (int): номер печи (1,2,3 or 4)

    Returns:
        P: (pd.DataFrame): прогноз расхода газа для печи 'furn_id' 
        для следующих 'distance' часов после последнего часа, приведенного
        в 'H'

    '''


    pass
    return P
