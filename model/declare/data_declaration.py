from biicode.common.utils.bii_logging import logger
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.exception import BiiException
import os
from biicode.common.model.declare.declaration import Declaration
from biicode.common.model.deps_props import DependenciesProperties


class DataDeclaration(Declaration):
    """Simple dependency solver. A dep name is a direct reference to the resource simbolic place.
       This is the case of text references or includes (c, cpp). Many dependencies could be solver
       through this simple algorithm.

    """
    def __init__(self, name):
        super(DataDeclaration, self).__init__(name)
        self.properties.add(DependenciesProperties.DATA)

    def match_system(self, system_cell_names):
        return set()

    def match(self, block_cell_names, origin_block_cell_name=None, paths=None):
        #Try absolute
        try:
            brl = BlockCellName(self.name)
            if brl in block_cell_names:
                return set([brl])
        except:
            pass

        #Try relative
        try:
            name = os.path.normpath(os.path.join(os.path.dirname(origin_block_cell_name),
                                                 self.name))
            brl = BlockCellName(name)
            if brl in block_cell_names:
                return set([brl])
        except:
            pass

        # Try APPROXIMATE, only in same block
        if origin_block_cell_name:
            try:
                block_name = origin_block_cell_name.block_name
                result = set()
                for name in block_cell_names:
                    if name.block_name == block_name:  # Approximate only find in same Block
                        if name.endswith(self.name):
                            tail = os.path.split(name)[1]
                            if len(self.name) >= len(tail):
                                result.add(name)

                if len(result) == 1:
                    return result

                #TODO: Inform user of multiple matchs
                logger.debug("Matchs for name %s are %s" % (self.name, result))
            except Exception as e:
                logger.error("Approximate find failed %s" % str(e))
                pass

        return set()

    def block(self):
        try:
            return BlockCellName(self.name).block_name
        except:
            return None

    def normalize(self, targets):
        if len(targets) != 1:
            raise BiiException("Incorrect input parameter %s" % targets)
        block_cell_name = iter(targets).next()
        return DataDeclaration(block_cell_name)
