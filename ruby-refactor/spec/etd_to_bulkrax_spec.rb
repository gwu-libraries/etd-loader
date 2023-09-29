require 'etd_to_bulkrax'

etd_sample = "test-diss.xml"

describe ETDParser do
    before do
        @etd_parser = ETDParser.new(etd_sample)
    end

    describe ".extract_authors" do
        context "given an XML with a primary author, first name, last name, middle name" do
            it "creates a single entry for the creator key" do
                @etd_parser.extract_authors
                expect(@etd_parser.bulkrax_doc["creator"]).to eq("N___, D___ J___")
            end
        end
    end

    describe ".get_title" do
        it "returns the title" do
            expect(@etd_parser.get_title).to eq("Prehospital Patient Triage: In Mass Casualty Incidents: An Engineering Management Analysis And Prototype Strategy Recommendation")
        end
    end

    describe ".get_date" do
        context "given an XML with a four-digit completion date" do
            it "returns the text" do
                expect(@etd_parser.get_date).to eq("2009")
            end
        end
    end

    describe ".extract_keywords" do
        context "given an XML with comma-separated keywords" do
            it "returns the keywords, semicolon-separated" do
                expect(@etd_parser.extract_keywords).to eq("Mass Casualty; Paramedics; PLUS; START; Triage")
            end
        end
    end

    describe ".extract_abstract" do
        context "given an XML with an abstract" do
            it "returns the text, joining paragraphs with line feeds and stripping any HTML tags" do
                abstract = @etd_parser.extract_abstract
                expect(abstract.slice(0, 20)).to eq("A significant triage")
                expect(abstract.length).to eq(2656)
            end
        end
    end

    describe ".get_affiliation" do
        context "given an XML with a single element for institutional contact" do
            it "returns the text" do
                expect(@etd_parser.get_affiliation).to eq("Engineering Mgt and Systems Engineering")
            end
        end
    end

    describe ".get_language" do
        context "given an XML with a single element for the language field" do
            it "returns the text" do
                expect(@etd_parser.get_language).to eq("en")
            end
        end
    end

    describe ".get_degree" do
        context "given an XML with a single element for the degree field" do
            it "returns the text" do
                expect(@etd_parser.get_degree).to eq("D.Sc.")
            end
        end
    end

    describe ".get_other_contribs" do
        context "given an XML with a single element for the advisor" do
            it "returns the name, last, first middle" do
                expect(@etd_parser.get_other_contribs).to eq("Harrald, John R.")
            end
        end
    end

    describe ".get_other_contribs" do
        context "given an XML with multiple elements for the cmte_member field" do
            it "returns the name, last, first middle of each element, separated by semicolons" do
                expect(@etd_parser.get_other_contribs("cmte_member")).to eq("Barbera, Joseph A.; Shaw, Greg; Fiedrich, Frank; Macintyre, Anthony")
            end
        end
    end

end