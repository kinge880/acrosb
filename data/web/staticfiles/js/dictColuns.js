// Dicionário de traduções das colunas
var columnTranslationDict = {
    'enviaemail': 'Enviar Email',
    'acumulativo': 'Acumulativo',
    'restringe_fornec': 'Fornecedor como restrição',
    'restringe_marca': 'Marca como restrição',
    'restringe_prod': 'Produto como restrição',
    'tipointensificador': 'Tipo de Intensificador',
    'usamarca': 'Marca como intensificador',
    'usafornec': 'Fornecedor como intensificador',
    'usaprod': 'Produto como intensificador',
    'multiplicador': 'Valor do intensificador',
    'marcavalor': 'Valor para intensificador por marca',
    'prodvalor': 'Valor para intensificador por produto',
    'fornecvalor': 'Valor para intensificador por fornecedor'
};

// Função para traduzir nomes das colunas
function translateColumnName(columnName) {
    return columnTranslationDict[columnName] || columnName;
}