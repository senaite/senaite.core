const interfaceTranslations = {
  selectedCountryAriaLabel: "País selecionado",
  noCountrySelected: "Nenhum país selecionado",
  countryListAriaLabel: "Lista de países",
  searchPlaceholder: "Procurar",
  clearSearchAriaLabel: "Limpar pesquisa",
  searchEmptyState: "Nenhum resultado encontrado",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Nenhum resultado encontrado";
    }
    if (count === 1) {
      return "1 resultado encontrado";
    }
    return `${count} resultados encontrados`;
  }
};
export default interfaceTranslations;
