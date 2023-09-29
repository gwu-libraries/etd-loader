require 'nokogiri'

class ETDParser

    attr_accessor :etd_doc, :bulkrax_doc

    def initialize(filename)
        @filename = filename
        @etd_doc = File.open(filename) { |f| Nokogiri::XML(f) }
        @bulkrax_doc = {}
    end

    def extract_full_name(node)
        surname = node.at_xpath("DISS_name/DISS_surname/text()")
        first_name = node.at_xpath("DISS_name/DISS_fname/text()")
        middle_name = node.at_xpath("DISS_name/DISS_middle/text()")
        middle_name ? "#{surname}, #{first_name} #{middle_name}" : "#{surname}, #{first_name}"
    end

    def extract_authors
        creators = []
        contributors = []
        @etd_doc.xpath("//DISS_authorship/DISS_author").each do |author_node|
            name = self.extract_full_name(author_node)
            if author_node.attr("type") == "primary"
                creators << name
            else
                contributors << name
            end
        end
        @bulkrax_doc["creator"] = creators.join("; ")
        @bulkrax_doc["contributor"] = contributors.join("; ")
    end   
    
    def get_title
        @etd_doc.at_xpath("//DISS_description/DISS_title/text()").text
    end

    def get_date
        date = @etd_doc.at_xpath("//DISS_description/DISS_dates/DISS_comp_date/text()").text
        date.length > 4 ? date.slice(0, 4) : date
    end

    def extract_keywords
        keywords = @etd_doc.at_xpath("//DISS_description/DISS_categorization/DISS_keyword/text()").text
        keywords.gsub(",", ";").gsub(":", ";").strip
    end

    def extract_abstract
        abs_text = []
        @etd_doc.xpath("//DISS_content/DISS_abstract/DISS_para/text()").each do |para|
            abs_text << para.text
        end
        abstract = Nokogiri::HTML(abs_text.join("\n")).text
        abstract
    end

    def get_affiliation
       @etd_doc.at_xpath("//DISS_description/DISS_institution/DISS_inst_contact/text()").text
    end
    
    def get_language
        @etd_doc.at_xpath("//DISS_description/DISS_categorization/DISS_language/text()").text
    end

    def get_degree
        @etd_doc.at_xpath("//DISS_description/DISS_degree/text()").text
    end

    def get_other_contribs(contrib_type="advisor")
        # contrib_type: adivsor|cmte_member
        contribs = []
        @etd_doc.xpath("//DISS_description/DISS_#{contrib_type}").each do |contrib|
            contribs << self.extract_full_name(contrib)
        end
        contribs.join("; ")
    end

end
